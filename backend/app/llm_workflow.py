from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_mistralai import ChatMistralAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START
from langgraph.graph import StateGraph

from app.rag import RAG
from database.database import Database
from datamodels.models import Character, State
from utils.consts import MISTRAL_LANGUAGE_MODEL


class LlmWorkflow:
    def __init__(self, character_id: int):
        """Initialize the ConversationalAgent with a specific character."""
        self.db = Database()
        self.character_id = character_id
        self.character = self.db.get_by_id(character_id, Character)
        self.llm = ChatMistralAI(model=MISTRAL_LANGUAGE_MODEL, streaming=True)
        self.rag = RAG()
        self.retriever = self.rag.retriever(character_id)
        self.graph = self._build_graph()

    def _get_system_prompt(self):
        """Returns a system prompt for the model with character's personality and context."""
        return (
            "<!--- Instruction Start -->\n"
            "## Task\n"
            "Adopt the personality described below and respond ONLY to the last message in conversation history. "
            "Consider the complete conversation history, the character's current location, situation, emotional state "
            "and goals below when writing a response. Consider the additional context ONLY if it is relevant "
            "for the conversation.\n"
            "Use three sentences maximum.\n"
            "## Name\n"
            f"{self.character.name}\n"
            "## Personality\n"
            f"{self.character.personality}\n"
            "## Context\n"
            "{context}\n\n"
            f"Respond as {self.character.name} and do NOT break character.\n"
            "<!--- Instruction End -->"
        )

    def _build_graph(self):
        """Build the conversational state graph and the retriever model pipeline."""
        # System and history-aware prompts
        system_prompt = self._get_system_prompt()

        contextualize_q_system_prompt = (
            "Given a chat history and the latest user input "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
        )

        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        # History-aware retriever
        history_aware_retriever = create_history_aware_retriever(
            self.llm, self.retriever, contextualize_q_prompt
        )

        # Question-answering prompt
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        # Chain for question-answering
        question_answer_chain = create_stuff_documents_chain(self.llm, qa_prompt)

        # Retrieval-augmented generation (RAG) chain
        rag_chain = create_retrieval_chain(
            history_aware_retriever, question_answer_chain
        )

        # Define the model call as a node in the graph
        async def call_model(state: State, config=None):
            response = await rag_chain.ainvoke(state, config)

            return {
                "chat_history": [
                    HumanMessage(state["input"]),
                    AIMessage(response["answer"]),
                ],
                "context": response["context"],
                "answer": response["answer"],
            }

        # Define the state graph and workflow
        workflow = StateGraph(state_schema=State)
        workflow.add_edge(START, "model")
        workflow.add_node("model", call_model)

        # Compile the graph with memory checkpointing
        memory = MemorySaver()
        graph = workflow.compile(checkpointer=memory)

        return graph

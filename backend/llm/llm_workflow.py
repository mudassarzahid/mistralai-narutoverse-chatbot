from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from langchain_mistralai import ChatMistralAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START
from langgraph.graph import StateGraph
from langgraph.types import StateSnapshot

from database.database import Database
from datamodels.models import Character, State
from llm.prompts import Prompts
from llm.rag import RAG
from utils.consts import MISTRAL_LANGUAGE_MODEL
from utils.logger import get_logger

logger = get_logger()


class LlmWorkflow:
    agents_store: dict[str, dict[int, "LlmWorkflow"]] = {}

    def __init__(self, character_id: int):
        """Initialize the ConversationalAgent with a specific character."""
        self.db = Database()
        self.character_id = character_id
        self.character = self.db.get_by_id(character_id, Character)

        self.llm = ChatMistralAI(model=MISTRAL_LANGUAGE_MODEL, streaming=True)
        self.rag = RAG()
        self.retriever = self.rag.retriever(character_id)

        self.graph = self._build_graph()

    def _get_summarized_personality(self, character_name: str, personality: str):
        res = self.llm.invoke(Prompts.get_summarize_personality(character_name, personality))
        print(res)
        return res.content

    def _build_graph(self):
        """Build the conversational state graph and the retriever model pipeline."""
        # System and history-aware prompts
        system_prompt = Prompts.get_system_prompt(
            self.character.name,
            self._get_summarized_personality(self.character.name, self.character.personality)
        )

        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", Prompts.get_contextualize_q_system_prompt()),
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

    def get_state(self, thread_id: str) -> StateSnapshot:
        config = self.get_config(thread_id)
        return self.graph.get_state(config)

    @staticmethod
    def get_config(thread_id: str) -> RunnableConfig:
        return RunnableConfig(
            **{"configurable": {"thread_id": thread_id}},
        )

    @classmethod
    def from_thread_id(cls, thread_id: str, character_id: int) -> "LlmWorkflow":
        """Retrieve or create a conversational agent based on the thread_id."""
        if thread_id not in cls.agents_store:
            logger.debug(f"Creating new agent for thread {thread_id}.")
            cls.agents_store[thread_id] = {character_id: LlmWorkflow(character_id)}
        else:
            if character_id not in cls.agents_store[thread_id]:
                cls.agents_store[thread_id][character_id] = LlmWorkflow(character_id)

        return cls.agents_store[thread_id][character_id]

from typing import Any, Optional

from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from langchain_mistralai import ChatMistralAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import StateSnapshot

from database.database import Database
from datamodels.models import Character, State
from llm.prompts import Prompts
from llm.rag import RAG
from utils.consts import MISTRAL_LANGUAGE_MODEL
from utils.logger import get_logger

logger = get_logger()


class LlmWorkflow:
    """Workflow class that statefully manages the conversation.

    Attributes:
        agents_store (dict): A store that maps thread IDs and character
            IDs to workflow instances.
        db (Database): Database instance for fetching character data.
        character_id (int): The ID of the character in the conversation.
        character (Character): The character fetched from the database.
        llm (ChatMistralAI): The language model used for conversation generation.
        retriever: The RAG retriever for the character data.
        graph (StateGraph): The runnable graph.
    """

    # TODO: This should be a database for persistence
    # Currently, chat histories are deleted after the server closes.
    agents_store: dict[str, dict[int, "LlmWorkflow"]] = {}

    def __init__(self, character_id: int):
        """Initialize the LlmWorkflow with a specific character and thread.

        Args:
            character_id (int): The ID of the character.
        """
        self.db = Database()
        self.character_id = character_id
        self.character = self.db.get_by_id(character_id, Character)

        self.llm = ChatMistralAI(model=MISTRAL_LANGUAGE_MODEL, streaming=True)
        self.retriever = RAG().retriever(character_id)
        self.graph = self._build_graph()

    def _get_summarized_personality(self) -> str:
        """Get or generate a summarized version of the character's personality.

        If the summarized personality exists, returns it. Otherwise,
        generates a summary using the language model and updates
        the character in the database.

        Returns:
            str: The summarized personality of the character.
        """
        if self.character.summarized_personality:
            return self.character.summarized_personality

        summarized_personality = self.llm.invoke(
            Prompts.get_summarize_personality_prompt(
                self.character.name,
                self.character.personality,
            )
        ).content

        self.db.update(
            self.character,
            {
                Character.summarized_personality.name: summarized_personality,  # type: ignore
            },
        )

        return summarized_personality

    def _build_graph(self) -> CompiledStateGraph:
        """Build the runnable graph and RAG-LLM pipeline.

        This includes setting up system prompts, history-aware retrievers,
        question-answering chains, and persistent memory management.

        Returns:
            StateGraph: The state graph representing the conversation flow.
        """
        # System and history-aware prompts
        system_prompt = Prompts.get_system_prompt(
            self.character.name,
            self._get_summarized_personality(),
        )

        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    Prompts.get_contextualize_q_system_prompt(self.character.name),
                ),
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

        # RAG chain
        rag_chain = create_retrieval_chain(
            history_aware_retriever, question_answer_chain
        )

        async def call_model(
            state: State, config: Optional[RunnableConfig] = None
        ) -> dict[str, Any]:
            """Invoke the language model with the current state and configuration.

            Args:
                state (State): The current conversation state.
                config (RunnableConfig, optional): Configuration for running the model.

            Returns:
                dict: The updated chat history, context, and answer.
            """
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
        """Retrieve the current state of the conversation.

        Args:
            thread_id (str): The ID of the conversation thread.

        Returns:
            StateSnapshot: The current snapshot of the conversation state.
        """
        config = self.get_config(thread_id)
        return self.graph.get_state(config)

    @staticmethod
    def get_config(thread_id: str) -> RunnableConfig:
        """Generate a configuration object based on the thread ID.

        Args:
            thread_id (str): The ID of the conversation thread.

        Returns:
            RunnableConfig: The configuration object for the conversation.
        """
        return {"configurable": {"thread_id": thread_id}}

    @classmethod
    def from_thread_id(cls, thread_id: str, character_id: int) -> "LlmWorkflow":
        """Retrieve or create a conversational agent based on the thread ID.

        If no agent exists for the thread, a new one is created. If an agent
        exists but not for the specified character, a new one for the character
        is created and added.

        Args:
            thread_id (str): The ID of the conversation thread.
            character_id (int): The ID of the character.

        Returns:
            LlmWorkflow: The workflow instance for the given character and thread.
        """
        if thread_id not in cls.agents_store:
            logger.debug(f"Creating new agent for thread {thread_id}.")
            cls.agents_store[thread_id] = {character_id: LlmWorkflow(character_id)}
        else:
            if character_id not in cls.agents_store[thread_id]:
                cls.agents_store[thread_id][character_id] = LlmWorkflow(character_id)

        return cls.agents_store[thread_id][character_id]

    @classmethod
    def get_character_ids_from_thread_id(cls, thread_id: str) -> list[int]:
        """Get a list of character IDs associated with a specific thread ID.

        Args:
            thread_id (str): The ID of the conversation thread.

        Returns:
            list[int]: A list of character IDs associated with the thread.
        """
        if thread_id not in cls.agents_store:
            return []
        return list(set(cls.agents_store[thread_id].keys()))

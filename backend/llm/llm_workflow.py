from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable, RunnableBinding, RunnableConfig
from langchain_mistralai import ChatMistralAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import StateSnapshot

from database.database import Database
from datamodels.enums import Sender
from datamodels.models import Character, State
from llm.prompts import Prompts
from llm.rag import RAG
from utils.consts import MISTRAL_LANGUAGE_MODEL_LARGE, MISTRAL_LANGUAGE_MODEL_MEDIUM
from utils.logger import get_logger

logger = get_logger()


class LlmWorkflow:
    """Workflow class that statefully manages the conversation.

    Attributes:
        agents_store (dict): A store that maps thread IDs and character
            IDs to workflow instances.
        db (Database): Database instance for fetching character data.
        character (Character): The character fetched from the database.
        retriever: The RAG retriever for the character data.
        graph (StateGraph): The runnable graph.
    """

    # TODO: This could be a database for persistence
    # Currently, chat histories are deleted if the server restarts.
    agents_store: dict[str, dict[int, "LlmWorkflow"]] = {}

    def __init__(self, character_id: int):
        """Initialize the LlmWorkflow with a specific character and thread.

        Args:
            character_id (int): The ID of the character.
        """
        self.db = Database()
        self.character = self.db.get_by_id(character_id, Character)
        self.retriever = RAG().retriever(character_id)
        self.graph = self._initialize_graph()
        self.prompts = Prompts(self.character)

    def _initialize_graph(self) -> CompiledStateGraph:
        """Initializes the state graph for managing conversation flow.

        Adds nodes and edges for tasks such as summarizing chat history,
        characterizing the user, and generating responses, and compiles
        the workflow with memory saving capabilities.

        Returns:
            CompiledStateGraph: The compiled workflow graph.
        """
        workflow = StateGraph(state_schema=State)
        workflow.add_node("summarize_chat_history", self._summarize_chat_history)
        workflow.add_node("characterize_user", self._characterize_user)
        workflow.add_node("model", self._generate_response)

        workflow.add_edge(START, "summarize_chat_history")
        workflow.add_edge("summarize_chat_history", "characterize_user")
        workflow.add_edge("characterize_user", "model")
        workflow.add_edge("model", END)

        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)

    def _get_summarized_personality_of_character(self) -> str:
        """Get or generate a summarized version of the character's personality.

        If the summarized personality exists, returns it. Otherwise,
        generates a summary using the language model and updates
        the character in the database.

        Returns:
            str: The summarized personality of the character.
        """
        if self.character.summarized_personality:
            return self.character.summarized_personality

        prompt = self.prompts.get_summarize_personality_prompt()
        llm = self.get_llm(MISTRAL_LANGUAGE_MODEL_MEDIUM)
        content = llm.invoke(prompt).content
        self.db.update(
            self.character,
            {
                Character.summarized_personality.name: content,  # type: ignore
            },
        )

        return content

    async def _summarize_chat_history(
        self, state: State, config: RunnableConfig
    ) -> State:
        """Summarizes the chat history to keep conversation context concise.

        Args:
            state (State): The current state of the workflow.
            config (RunnableConfig): Configuration for the runnable.

        Returns:
            State: The updated state with summarized chat history.
        """
        prompt = self.prompts.get_summarize_chat_history_prompt(state)
        llm = self.get_llm(MISTRAL_LANGUAGE_MODEL_LARGE)
        content = llm.invoke(prompt, config).content
        state["chat_summary"] = content

        return state

    async def _characterize_user(self, state: State, config: RunnableConfig) -> State:
        """Generates a characterization of the user based on conversation data.

        Args:
            state (State): The current workflow state.
            config (RunnableConfig): Configuration for the runnable.

        Returns:
            State: The updated state with user characterization.
        """
        user_info_prompt = self.prompts.get_characterize_user_prompt(state)
        llm = self.get_llm(MISTRAL_LANGUAGE_MODEL_LARGE)
        content = llm.invoke(user_info_prompt, config).content
        state["user_information"] = content

        return state

    async def _generate_response(self, state: State, config: RunnableConfig) -> State:
        """Generates a response using the RAG chain and conversation context.

        Args:
            state (State): The current workflow state.
            config (RunnableConfig): Configuration for the runnable.

        Returns:
           State: The updated state with conversation context.
        """
        response = await self._rag_chain(state, config).ainvoke(state, config)
        return State(
            input=state["input"],
            chat_history=[
                HumanMessage(response["input"]),
                AIMessage(response["answer"]),
            ],
            chat_summary=response["chat_summary"],
            context=response["context"],
            answer=response["answer"],
            user_information=response["user_information"],
        )

    def _rag_chain(self, state: State, _config: RunnableConfig) -> RunnableBinding:
        """Builds the RAG-LLM pipeline with retrieval and memory management.

        Sets up a retrieval-chat-chain for context-aware conversations
        using character data and prior conversation history.

        Args:
            state (State): The current workflow state.
            _config (RunnableConfig): Configuration for the runnable.

        Returns:
            Runnable: The complete RAG-LLM conversation chain.
        """
        # Instruct AI how to respond
        system_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    Sender.system,
                    self.prompts.get_system_prompt(
                        self._get_summarized_personality_of_character(),
                    ),
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                (Sender.human, "{input}"),
            ]
        )
        llm_large = self.get_llm(MISTRAL_LANGUAGE_MODEL_LARGE, streaming=True)
        chat_chain = create_stuff_documents_chain(llm_large, system_prompt)

        contextualize_prompt = ChatPromptTemplate.from_messages(
            [
                (Sender.human, "{input}"),
                (
                    Sender.system,
                    self.prompts.get_contextualize_q_system_prompt(state),
                ),
            ]
        )
        llm_medium = self.get_llm(MISTRAL_LANGUAGE_MODEL_MEDIUM)
        history_aware_retriever = create_history_aware_retriever(
            llm_medium,
            self.retriever,
            contextualize_prompt,
        )
        return create_retrieval_chain(history_aware_retriever, chat_chain)

    def get_state(self, thread_id: str) -> StateSnapshot:
        """Retrieve the current state of the conversation.

        Args:
            thread_id (str): The ID of the conversation thread.

        Returns:
            StateSnapshot: The current snapshot of the conversation state.
        """
        return self.graph.get_state(self._get_config(thread_id))

    @staticmethod
    def _get_config(thread_id: str) -> RunnableConfig:
        """Generate a configuration object based on the thread ID.

        Args:
            thread_id (str): The ID of the conversation thread.

        Returns:
            RunnableConfig: The configuration object for the conversation.
        """
        return RunnableConfig(configurable={"thread_id": thread_id})

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
            cls.agents_store[thread_id] = {}
        if character_id not in cls.agents_store[thread_id]:
            cls.agents_store[thread_id][character_id] = cls(character_id)
        return cls.agents_store[thread_id][character_id]

    @classmethod
    def get_chat_character_ids(cls, thread_id: str) -> list[int]:
        """Get a list of character IDs associated with a specific thread ID.

        Args:
            thread_id (str): The ID of the conversation thread.

        Returns:
            list[int]: A list of character IDs associated with the thread.
        """
        return list(cls.agents_store.get(thread_id, {}).keys())

    @classmethod
    def delete_character_chat_history(cls, thread_id: str, character_id: int) -> None:
        """Delete the chat history with a specific character for a thread.

        Args:
            thread_id (str): The ID of the conversation thread.
            character_id (int): The ID of the character.

        Returns:
            list[int]: A list of character IDs associated with the thread.
        """
        cls.agents_store.get(thread_id, {}).pop(character_id, None)

    @staticmethod
    def get_llm(model_name: str, streaming: bool = False) -> ChatMistralAI:
        """Get an instance of the specified language model.

        Args:
            model_name (str): The name of the language model.
            streaming (bool, optional): Indicates if streaming mode is enabled.

        Returns:
            ChatMistralAI: An instance of the specified language model.
        """
        return ChatMistralAI(model=model_name, streaming=streaming)

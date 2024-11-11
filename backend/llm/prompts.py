from langchain_core.messages import HumanMessage

from datamodels.enums import Sender
from datamodels.models import Character, State


class Prompts:
    """A utility class for generating prompts."""

    def __init__(self, character: Character):
        """Initialize Prompts instance with character-specific prompts.

        Args:
            character (Character): The character to generate prompts for.
        """
        self.character = character

    def get_system_prompt(self) -> str:
        """Generates a system prompt for impersonating a character based on context.

        Returns:
            str: A system prompt that instructs the LLM to adopt
                the character's personality.
        """
        return (
            "## Character Name\n"
            f"{self.character.name}\n"
            "## Character Personality\n"
            f"{self.character.summarized_personality}\n"
            "## Human Personality\n"
            "{user_information}"
            "## Context\n"
            "{context}\n\n"
            "## Task\n"
            f"You are {self.character.name} and talking to a human Adopt the "
            f"{self.character.name}'s personality described above and "
            "respond to the last message in conversation history. Consider the "
            f"complete conversation history, the {self.character.name}'s "
            "current location, situation, emotional state, goals, personality "
            "and quirks when writing a response. Consider the additional "
            "context ONLY if it is relevant for the conversation.\n\n"
            f"Respond as {self.character.name} and use three sentences maximum. "
            f"Do NOT break character.\n"
        )

    def get_contextualize_q_system_prompt(self, state: State) -> str:
        """Generates a system prompt to contextualize the user query.

        The contextualized prompt is used to query the vectorDB.

        Args:
            state (State): The state langgraph.

        Returns:
            str: A system prompt for generating search queries
                relevant to the conversation.
        """
        chat_summary = state.get("chat_summary", "<empty>")
        formatted_history = self._format_chat_history(state, last_n=2)
        return (
            f"## Chat history between a human and {self.character.name}\n"
            f"{chat_summary}\n{formatted_history}\n\n"
            "## Task"
            "You are a machine that ONLY generates short search queries. "
            "Given the above conversation, generate a search query to "
            "look up in order to get information relevant to the conversation. "
        )

    def get_summarize_personality_prompt(self) -> str:
        """Generates a prompt to summarize a character's personality.

        Returns:
            str: A system prompt for summarizing the character's
                personality concisely.
        """
        return (
            f"## {self.character.name}'s personality\n"
            f"{self.character.personality}\n"
            "## Task\n"
            f"Summarize the personality description of {self.character.name} "
            "from 'Naruto'. Make sure to include all distinctive "
            "character traits and quirks but also keep it concise and as "
            "short as possible."
        )

    def get_summarize_chat_history_prompt(self, state: State) -> str:
        """Generates a prompt to summarize the chat history.

        Args:
            state (State): The state of the langgraph.

        Returns:
            str: A system prompt for summarizing the chat history.
        """
        chat_summary = state.get("chat_summary", "<empty>")
        formatted_history = self._format_chat_history(state, last_n=2)
        return (
            f"## Chat history between a human and {self.character.name}\n"
            f"{chat_summary}\n{formatted_history}\n"
            "## Task\n"
            "Summarize the chat history. Keep it short and concise."
        )

    def get_characterize_user_prompt(self, state: State) -> str:
        """Generates a prompt to characterize the user.

        Args:
            state (State): The state of the langgraph.

        Returns:
            str: A system prompt for characterizing the user.
        """
        user_information = state.get("user_information", "a complete stranger")
        chat_summary = state.get("chat_summary", "<empty>")
        formatted_history = self._format_chat_history(state, last_n=2)
        return (
            f"## Chat history between a human and {self.character.name}\n"
            f"{chat_summary}\n{formatted_history}\n"
            f"## Characterization of the human\n"
            f"{user_information}\n"
            "Update the human's personality description in a short and "
            "concise way and based ONLY on the available information."
        )

    def _format_chat_history(self, state: State, last_n=0) -> str:
        """Utility function for generating a string of chat history.

        Args:
            state (State): The state of the langgraph.
            last_n (int, optional): The last n messages to show in the chat history.

        Returns:
            str: A string of chat history.
        """
        history = (
            [
                (
                    f"{Sender.human}: {msg.content}"
                    if isinstance(msg, HumanMessage)
                    else f"{self.character.name}: {msg.content}"
                )
                for msg in state["chat_history"][last_n:]
            ]
            if len(state["chat_history"]) > 1
            else []
        )
        return "\n".join(history + [f"{Sender.human}: {state['input']}"])

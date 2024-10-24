class Prompts:
    """A utility class for generating prompts."""

    @staticmethod
    def get_system_prompt(character_name: str, character_personality: str) -> str:
        """Generates a system prompt for impersonating a character based on context.

        Args:
            character_name (str): The name of the character.
            character_personality (str): A description of the character's personality.

        Returns:
            str: A system prompt that instructs the LLM to adopt
                the character's personality.
        """
        return (
            "<!--- Instruction Start -->\n"
            "## Task\n"
            f"You are {character_name} and talking to a complete stranger. Adopt the "
            "personality described below and respond to the last message in conversation "
            "history. Consider the complete conversation history, the character's "
            "current location, situation, emotional state, goals, personality and quirks "
            "when writing a response. Consider the additional context ONLY if it is "
            "relevant for the conversation.\n\n"
            "## Name\n"
            f"{character_name}\n"
            "## Personality\n"
            f"{character_personality}\n"
            "## Context\n"
            "<!--- Context Start -->\n"
            "{context}\n\n"
            "<!--- Context End -->\n"
            f"Respond as {character_name} and use three sentences maximum. "
            f"Do NOT break character.\n"
            "<!--- Instruction End -->"
        )

    @staticmethod
    def get_contextualize_q_system_prompt(character_name: str) -> str:
        """Generates a system prompt to contextualize the user query.

        The contextualized prompt is used to query the vectorDB.

        Args:
            character_name (str): The name of the character.

        Returns:
            str: A system prompt for generating search queries
                relevant to the conversation.
        """
        return (
            "Given the above conversation, generate ONLY a search query to "
            "look up in order to get information relevant to the conversation. "
            f"Important: The pronoun 'You' refers to {character_name}. "
            "\nQuery:"
        )

    @staticmethod
    def get_summarize_personality_prompt(character_name: str, personality: str) -> str:
        """Generates a prompt to summarize a character's personality.

        Args:
            character_name (str): The name of the character.
            personality (str): A detailed description of the
                character's personality (from NarutoWiki).

        Returns:
            str: A system prompt for summarizing the character's
                personality concisely.
        """
        return (
            f"Summarize the personality description of {character_name} "
            "from 'Naruto' below. Make sure to include all distinctive "
            "character traits and quirks but also keep it concise and as "
            f"short as possible.\nPersonality: {personality}"
        )

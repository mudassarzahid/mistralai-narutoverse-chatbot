class Prompts:
    @staticmethod
    def get_system_prompt(character_name: str, character_personality: str) -> str:
        """Returns a system prompt for the model with character's personality and context."""
        return (
            "<!--- Instruction Start -->\n"
            "## Task\n"
            "Adopt the personality described below and respond to the last USER message "
            "in conversation history. The USER is a total stranger to you. "
            "Consider the complete conversation history, the character's current "
            "location, situation, emotional state and goals when writing a response. "
            "Consider the additional context ONLY if it is relevant for the conversation.\n\n"
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
        return (
            "Given the above conversation, generate a search query to "
            "look up in order to get information relevant to the conversation. "
            f"IMPORTANT: 'You' always refers to the character {character_name}!"
        )

    @staticmethod
    def get_summarize_personality_prompt(character_name: str, personality: str) -> str:
        return (
            f"Summarize the personality description of {character_name} "
            "from 'Naruto' below. Make sure to include all distinctive "
            "character traits and quirks but also keep it concise and as "
            f"short as possible.\nPersonality: {personality}"
        )

class Prompts:
    @staticmethod
    def get_system_prompt(character_name: str, character_personality: str):
        """Returns a system prompt for the model with character's personality and context."""
        return (
            "<!--- Instruction Start -->\n"
            "## Task\n"
            "Adopt the personality described below and respond ONLY to the last message "
            "in conversation history. Consider the complete conversation history, the "
            "character's current location, situation, emotional state and goals below "
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
    def get_contextualize_q_system_prompt():
        return (
            "Given a chat history and the latest user input "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
        )

    @staticmethod
    def get_summarize_personality_prompt(character_name: str, personality: str):
        return (
            f"Summarize the personality description of {character_name} "
            f"from 'Naruto' below. Make sure to include all distinctive "
            f"character traits and quirks but also keep it concise and as "
            f"short as possible.\nPersonality: {personality}"
        )

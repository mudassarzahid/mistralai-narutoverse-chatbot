from enum import Enum


class Sender(str, Enum):
    """Enum for message senders."""

    human = "human"
    ai = "ai"
    system = "system"

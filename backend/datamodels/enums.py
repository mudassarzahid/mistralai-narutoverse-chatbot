from enum import Enum


class Sender(str, Enum):
    """Enum for message senders."""

    user = "user"
    bot = "bot"

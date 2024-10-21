from enum import Enum


class Sender(str, Enum):
    user = "user"
    bot = "bot"

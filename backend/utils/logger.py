import logging
import logging.handlers
import os

from utils.consts import LOGS_DIR


def get_logger(
    name: str = "default",
    level: int = logging.DEBUG,
) -> logging.Logger:
    """
    Get a logger with the specified name, log file, and level.

    Args:
        name (str): The name of the logger.
        level (int): The logging level (e.g., logging.DEBUG, logging.INFO).

    Returns:
        logging.Logger: The configured logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Ensure log file directory exists
    os.makedirs(LOGS_DIR, exist_ok=True)

    # Create file handler that logs to a file
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(LOGS_DIR, f"{name}.log"),
        maxBytes=1024 * 1024 * 5,
        backupCount=3,
    )
    file_handler.setLevel(level)

    # Create a logging format
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-5s | %(name)s | %(message)s"
    )
    file_handler.setFormatter(formatter)

    # Add the handlers to the logger if not already added
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(logging.StreamHandler())

    return logger

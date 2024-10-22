from http import HTTPStatus

from fastapi import HTTPException


class NotFoundError(HTTPException):
    """Exception raised when a requested DB resource is not found.

    Attributes:
        message (str): A detailed description of the error.
    """

    def __init__(self, detail: str):
        """Initializes NotFoundError with a detail message.

        Args:
            detail (str): The error message.
        """
        self.message = detail
        super(HTTPException, self).__init__(HTTPStatus.NOT_FOUND, detail)


class EmbeddingsNotCreatedError(HTTPException):
    """Exception raised when embeddings fail to be created.

    This exception is used to signal an issue with generating
    embeddings, e.g. when the MistralAI backend is unreachable
    or fails to process the request.

    Attributes:
        message (str): A detailed description of the error.
    """

    def __init__(self, detail: str):
        """Initializes EmbeddingsNotCreatedError with a detail message.

        Args:
            detail (str): The error message.
        """
        self.message = detail
        super(HTTPException, self).__init__(HTTPStatus.INTERNAL_SERVER_ERROR, detail)

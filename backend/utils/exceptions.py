from http import HTTPStatus

from fastapi import HTTPException


class NotFoundError(HTTPException):
    def __init__(self, detail):
        self.message = detail
        super(HTTPException, self).__init__(HTTPStatus.NOT_FOUND, detail)


class EmbeddingsNotCreatedError(HTTPException):
    def __init__(self, detail):
        self.message = detail
        super(HTTPException, self).__init__(HTTPStatus.INTERNAL_SERVER_ERROR, detail)

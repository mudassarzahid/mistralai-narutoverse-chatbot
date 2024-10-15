from http import HTTPStatus
from typing import Any, Sequence

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routes import router
from database.database import bulk_insert_characters, create_db_and_tables, is_db_empty
from scraper.scraper import NarutoWikiScraper

app = FastAPI()
app.include_router(router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Custom exception handler for handling FastAPI RequestValidationErrors.

    Pydantic models throw RequestValidationErrors when validation errors occur.

    Args:
        _: FastAPI Request object (unused).
        exc (RequestValidationError): The raised RequestValidationError.

    Returns:
        JSONResponse: A JSON response containing information about the validation errors.
    """
    errors: Sequence[dict[str, Any]] = exc.errors()
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            {
                "message": f"An error occurred: {exc.__class__.__name__}",
                "details": errors,
            }
        ),
    )


@app.on_event("startup")
async def on_startup():
    create_db_and_tables()
    if is_db_empty():
        scraper = NarutoWikiScraper()
        characters = await scraper.fetch_all_characters()
        bulk_insert_characters(characters)


app.include_router(router)

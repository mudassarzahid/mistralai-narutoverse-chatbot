from fastapi import FastAPI

from app.routes import router
from database.database import (
    bulk_insert_characters,
    create_db_and_tables,
)
from scraper.scraper import fetch_all_characters

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    create_db_and_tables()
    characters = await fetch_all_characters()
    bulk_insert_characters(characters)


app.include_router(router)

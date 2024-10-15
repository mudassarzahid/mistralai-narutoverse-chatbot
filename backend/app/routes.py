from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Request

from database.database import Database
from datamodels.models import Character, GetCharactersQueryParams

router = APIRouter()
db = Database()


@router.on_event("startup")
async def on_startup():
    db.create_db_and_tables()
    await db.scrape_all_characters()


@router.post("/characters/")
def create_character(character: Character) -> Character:
    return db.create(character)


@router.get("/characters")
def get_characters(request: Request) -> list[dict[str, Any]]:
    params = GetCharactersQueryParams.from_request(request)
    return db.get(params)


@router.get("/characters/{character_id}")
def read_character(character_id: int) -> Character:
    return db.get_by_id(character_id, Character)


@router.delete("/characters/{character_id}")
def delete_character(character_id: int):
    db.delete_by_id(character_id, Character)
    return {"status": HTTPStatus.ACCEPTED}

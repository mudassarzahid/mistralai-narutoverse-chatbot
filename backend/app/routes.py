from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from database.database import get_session
from datamodels.models import Character

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_session)]


@router.post("/characters/")
def create_character(character: Character, session: SessionDep) -> Character:
    session.add(character)
    session.commit()
    session.refresh(character)
    return character


@router.get("/characters/")
def read_characters(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Character]:
    characters = session.exec(select(Character).offset(offset).limit(limit)).all()
    return characters


@router.get("/characters/{character_id}")
def read_character(character_id: int, session: SessionDep) -> Character:
    character = session.get(Character, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character


@router.delete("/characters/{character_id}")
def delete_character(character_id: int, session: SessionDep):
    character = session.get(Character, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    session.delete(character)
    session.commit()
    return {"ok": True}

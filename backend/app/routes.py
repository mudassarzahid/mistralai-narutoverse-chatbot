from typing import Annotated, Any, Sequence

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import column, text
from sqlalchemy.orm import load_only
from sqlmodel import Session, select

from database.database import get_characters, get_session
from datamodels.models import Character, GetCharactersQueryParams

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_session)]


@router.post("/characters/")
def create_character(character: Character, session: SessionDep) -> Character:
    session.add(character)
    session.commit()
    session.refresh(character)
    return character


@router.get("/characters")
def get_characters(
    request: Request,
    session: SessionDep = None,
) -> Any:
    params = GetCharactersQueryParams.from_request(request)
    columns = [getattr(Character, col) for col in params.columns]
    result = session.exec(
        select(*columns).offset(params.offset).limit(params.limit)
    ).all()

    rows = []
    for row in result:
        # If only one column is selected the row type is string
        if type(row) is str:
            rows.append({params.columns[0]: row})
        else:
            rows.append(dict(zip(params.columns, row)))

    return rows


@router.get("/characters/search")
def search_characters(
    request: Request,
    session: SessionDep,
) -> list[dict[str, Any]]:
    filters = dict(request.query_params)
    characters = get_characters(filters=filters, model=Character)

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

from typing import Annotated, Optional

from fastapi import Query, Request
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class QueryParams(BaseModel):
    offset: int = 0
    limit: Annotated[int, Query(le=100)] = 100


class GetCharactersQueryParams(QueryParams):
    columns: Optional[list[str]]

    @classmethod
    def from_request(cls, request: Request) -> "GetCharactersQueryParams":
        params = dict(request.query_params)
        columns = request.query_params.getlist("columns")
        valid_columns = list(Character.model_fields.keys())

        if not set(columns).issubset(set(valid_columns)):
            raise RequestValidationError(
                f"{columns=} must be a subset of {valid_columns=}."
            )

        if not columns:
            columns = valid_columns

        params["columns"] = columns

        return GetCharactersQueryParams(**params)


class CharacterData(BaseModel):
    text: str
    tag_1: str
    tag_2: str | None = Field(default=None)
    tag_3: str | None = Field(default=None)


class Character(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    href: str | None = Field(default=None, index=True)
    image_url: str | None = Field(default=None)
    summary: str | None = Field(default=None)
    data: list[CharacterData] = Field(default_factory=list, sa_column=Column(JSON))


class Story(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    href: str | None = Field(default=None, index=True)

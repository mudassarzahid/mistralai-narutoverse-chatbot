from typing import Annotated, Any, Optional

from fastapi import Query, Request
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from sqlalchemy import JSON, Column, SQLColumnExpression, func
from sqlalchemy.orm import InstrumentedAttribute
from sqlmodel import Field, SQLModel


class QueryParams(BaseModel):
    offset: int = 0
    limit: Annotated[int, Query(le=100)] = 100


class GetCharactersQueryParams(QueryParams):
    columns: Optional[list[SQLColumnExpression | InstrumentedAttribute]] = None
    order_by: Optional[list[SQLColumnExpression | InstrumentedAttribute]] = None

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_request(cls, request: Request) -> "GetCharactersQueryParams":
        params = dict(request.query_params)

        # select columns
        columns = request.query_params.getlist("columns")
        valid_columns = list(Character.model_fields.keys())
        if not set(columns).issubset(set(valid_columns)):
            raise RequestValidationError(
                f"{columns=} must be a subset of {valid_columns=}."
            )
        if not columns:
            params["columns"] = [getattr(Character, col) for col in valid_columns]
        else:
            params["columns"] = [getattr(Character, col) for col in columns]

        # order by conditions
        order_by_conditions = request.query_params.getlist("order_by")
        valid_order_by_conditions = valid_columns + ["relevance"]
        if not set(order_by_conditions).issubset(set(valid_order_by_conditions)):
            raise RequestValidationError(
                f"{order_by_conditions=} must be a subset of {valid_order_by_conditions=}."
            )
        params["order_by"] = []
        for condition in order_by_conditions:
            if condition == "relevance":
                params["order_by"].append(func.length(Character.data).desc())
            else:
                params["order_by"].append(getattr(Character, condition))

        return GetCharactersQueryParams(**params)


class CharacterData(BaseModel):
    text: str
    tag_1: str
    tag_2: Optional[str] = Field(default=None)
    tag_3: Optional[str] = Field(default=None)


class Character(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # auto-incremented
    name: str = Field(index=True)
    href: str = Field(default=None, index=True)
    image_url: Optional[str] = Field(default=None)
    summary: str = Field(default=None)
    data: list[CharacterData] = Field(
        default_factory=list[dict[str, Any]], sa_column=Column(JSON)
    )


class Story(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    href: str | None = Field(default=None, index=True)

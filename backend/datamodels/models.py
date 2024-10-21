from typing import Any, Optional, Sequence

from fastapi import Query, Request
from fastapi.exceptions import RequestValidationError
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel
from sqlalchemy import JSON, Column, UnaryExpression
from sqlalchemy.orm import InstrumentedAttribute
from sqlmodel import Field, SQLModel
from typing_extensions import Annotated, TypedDict


class QueryParams(BaseModel):
    offset: int = 0
    limit: Annotated[int, Query(le=100)] = 100


class GetCharactersParams(QueryParams):
    columns: Optional[list[InstrumentedAttribute | UnaryExpression]] = None
    order_by: Optional[list[InstrumentedAttribute | UnaryExpression]] = None
    asc: Optional[bool] = True

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_request(cls, request: Request) -> "GetCharactersParams":
        params: dict[str, Any] = dict(request.query_params)
        valid_columns = list(Character.model_fields.keys())
        select_columns = request.query_params.getlist("columns")
        order_by_columns = request.query_params.getlist("order_by")

        # Validate and set columns
        columns = cls._get_validated_columns(select_columns, valid_columns)
        order_by_columns = cls._get_validated_columns(order_by_columns, valid_columns)
        desc = params.get("asc", "true").lower() == "false"
        params["asc"] = not desc
        params["columns"] = [getattr(Character, col) for col in columns]
        params["order_by"] = [
            getattr(Character, col) if params["asc"] else getattr(Character, col).desc()
            for col in (order_by_columns or columns)
        ]

        return cls(**params)

    @staticmethod
    def _get_validated_columns(
        columns: list[str], valid_columns: list[str]
    ) -> list[str]:
        query_columns = columns or valid_columns
        query_columns_set = set(query_columns)
        valid_columns_set = set(valid_columns)
        if not query_columns_set.issubset(valid_columns_set):
            raise RequestValidationError(
                f"{query_columns_set=} must be a subset of {valid_columns_set=}."
            )
        return columns


class GetChatHistoryParams(QueryParams):
    thread_id: str
    character_id: int


class CharacterData(BaseModel):
    text: str
    tag_1: str
    tag_2: Optional[str] = Field(default=None)
    tag_3: Optional[str] = Field(default=None)


class Character(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    href: str = Field(default=None, index=True)
    image_url: Optional[str] = Field(default=None)
    summary: str = Field(default=None)
    personality: str = Field(default=None)
    data: list[dict[str, Any]] = Field(
        default_factory=list[CharacterData],
        sa_column=Column(JSON),
    )
    data_length: int = Field(default=None)


class Story(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    href: str = Field(default=None, index=True)


class EmbeddingMapping(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    character_id: int = Field(default=None, index=True, foreign_key="character.id")


class DocumentMetadata(BaseModel):
    character_id: int
    source: Optional[str] = "NarutoWiki"
    name: str
    tag_1: str
    tag_2: Optional[str] = "null"
    tag_3: Optional[str] = "null"


# Using TypedDict instead of pydantic for easier integration
# with langchain (same input and output keys as `rag_chain`).
class State(TypedDict):
    input: str
    chat_history: Annotated[Sequence[BaseMessage], add_messages]
    context: str
    answer: str

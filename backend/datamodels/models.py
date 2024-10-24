from typing import Any, Optional, Sequence

from fastapi import Query, Request
from fastapi.exceptions import RequestValidationError
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, model_validator
from sqlalchemy import JSON, Column, UnaryExpression
from sqlalchemy.orm import InstrumentedAttribute
from sqlmodel import Field, SQLModel
from typing_extensions import Annotated, TypedDict

from datamodels.enums import Sender


class QueryParams(BaseModel):
    """Base model for query parameters with pagination support.

    Attributes:
        offset (int): The starting point for the query results. Defaults to 0.
        limit (int): The number of results to return. Defaults to 100 (maximum).
    """

    offset: int = 0
    limit: Annotated[int, Query(le=100)] = 100


class GetCharactersParams(QueryParams):
    """Model for query parameters when fetching character data.

    Attributes:
        columns (Optional[list]): The list of columns to select.
        order_by (Optional[list]): The list of columns to order by.
        asc (Optional[bool]): Whether to order results in ascending
            order. Defaults to True.
    """

    columns: Optional[list[InstrumentedAttribute | UnaryExpression]] = None
    order_by: Optional[list[InstrumentedAttribute | UnaryExpression]] = None
    asc: Optional[bool] = True

    class Config:
        """Config to allow arbitrary field types."""

        arbitrary_types_allowed = True

    @classmethod
    def from_request(cls, request: Request) -> "GetCharactersParams":
        """Parses query parameters from a request.

        Args:
            request (Request): The FastAPI request object.

        Returns:
            GetCharactersParams: An instance of the class populated with query parameters.

        Raises:
            RequestValidationError: If invalid columns are given.
        """
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
        """Validates selected columns against valid columns.

        Args:
            columns (list[str]): List of columns to validate.
            valid_columns (list[str]): List of valid column names.

        Returns:
            list[str]: A list of validated columns.

        Raises:
            RequestValidationError: If invalid columns are provided.
        """
        query_columns = columns or valid_columns
        query_columns_set = set(query_columns)
        valid_columns_set = set(valid_columns)
        if not query_columns_set.issubset(valid_columns_set):
            raise RequestValidationError(
                f"{query_columns_set=} must be a subset of {valid_columns_set=}."
            )
        return query_columns


class CharacterData(BaseModel):
    """Model representing character-related data.

    Attributes:
        text (str): The main text.
        tag_1 (str): The primary tag associated with the content.
        tag_2 (Optional[str]): The second tag (optional).
        tag_3 (Optional[str]): The third tag (optional).
    """

    text: str
    tag_1: str
    tag_2: Optional[str] = Field(default=None)
    tag_3: Optional[str] = Field(default=None)


class CharacterCreate(BaseModel):
    """Request model for creating a new character in the db.

    Attributes:
        name (str): The name of the character.
        href (str): The NarutoWiki link of the character.
        image_url (Optional[str]): The URL of the character's image.
        summary (str): A summary of the character.
        personality (str): A description of the character's personality.
        summarized_personality (Optional[str]): A summary of the personality.
        data (Optional[list[CharacterData]]): A list of character-related data sections.
        data_length (Optional[int]): The total length of all text data combined.
    """

    name: str
    href: str
    image_url: Optional[str] = None
    summary: str
    personality: str
    summarized_personality: Optional[str] = None
    data: Optional[list[CharacterData]] = []
    data_length: Optional[int] = 0

    @model_validator(mode="before")
    @classmethod
    def calculate_data_length(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Calculates and updates the total length of the text sections.

        Args:
            data (dict[str, Any]): The character creation data.

        Returns:
            dict[str, Any]: The updated data with the computed `data_length`.
        """
        data.update(
            {
                "data_length": sum(
                    [len(section["text"]) for section in data.get("data", [])]
                )
            }
        )
        return data


class Character(SQLModel, table=True):
    """SQLModel representation of a Character entity.

    Attributes:
        id (Optional[int]): The character's unique identifier.
        name (str): The character's name.
        href (str): The NarutoWiki link of the character.
        image_url (Optional[str]): The URL to the character's image.
        summary (str): A summary of the character.
        personality (str): A description of the character's personality.
        summarized_personality (Optional[str]): A summary of the personality.
        data (list[dict[str, Any]]): A list of associated data.
        data_length (int): The total length of the character's associated text data.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    href: str = Field(index=True)
    image_url: Optional[str] = Field(default=None)
    summary: str = Field(default=None)
    personality: str = Field(default=None)
    summarized_personality: Optional[str] = Field(default=None)
    data: list[dict[str, Any]] = Field(
        default_factory=list[CharacterData],
        sa_column=Column(JSON),
    )
    data_length: int = Field(default=None)


class EmbeddingLog(SQLModel, table=True):
    """SQLModel for tracking if a character's embeddings have been created.

    Attributes:
        id (Optional[int]): The ID of the row.
        character_id (int): The ID of the associated character.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    character_id: int = Field(default=None, index=True, foreign_key="character.id")


class DocumentMetadata(BaseModel):
    """Metadata model for documents associated with characters.

    This metadata is stored in the vectorDB and can be used
    for filtering.

    Attributes:
        character_id (int): The ID of the associated character.
        source (Optional[str]): The source of the document. Defaults to 'NarutoWiki'.
        name (str): The name of the character.
        tag_1 (str): The primary tag associated with the document.
        tag_2 (Optional[str]): The second tag. Defaults to 'null'.
        tag_3 (Optional[str]): The third tag. Defaults to 'null'.
    """

    character_id: int
    source: Optional[str] = "NarutoWiki"
    name: str
    tag_1: str
    tag_2: Optional[str] = "null"
    tag_3: Optional[str] = "null"


class Message(BaseModel):
    """Model representing a message in a chat.

    Attributes:
        sender (Sender): The entity sending the message (user or bot).
        text (str): The message content.
    """

    sender: Sender
    text: str


class State(TypedDict):
    """TypedDict representing the state of a conversation.

    A TypedDict instead of pydantic model is used for easier
    integration with langchain (same input and output keys as
    `rag_chain`).

    Attributes:
        input (str): The input from the user.
        chat_history (Annotated[Sequence[BaseMessage], add_messages]):
            The history of the chat.
        context (str): The current context of the conversation.
        answer (str): The generated answer based on the conversation.
    """

    input: str
    chat_history: Annotated[Sequence[BaseMessage], add_messages]
    context: str
    answer: str

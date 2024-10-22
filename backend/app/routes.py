from http import HTTPStatus
from typing import Any, AsyncGenerator

from fastapi import APIRouter, Body, Request
from langchain_core.messages import AIMessageChunk, HumanMessage
from starlette.responses import StreamingResponse

from database.database import Database
from datamodels.enums import Sender
from datamodels.models import (
    Character,
    CharacterCreate,
    GetCharactersParams,
    GetChatHistoryParams,
    GetChatsParams,
    Message,
)
from llm.llm_workflow import LlmWorkflow
from scraper.scraper import NarutoWikiScraper
from utils.logger import get_logger

router = APIRouter()
db = Database()
logger = get_logger()


@router.on_event("startup")
async def on_startup() -> None:
    """Scrapes all Naruto characters on startup."""
    scraper = NarutoWikiScraper()
    await scraper.scrape_all_characters()


@router.post("/characters", status_code=HTTPStatus.CREATED)
def create_character(character_create: CharacterCreate) -> Character:
    """Creates a new character in the database.

    Args:
        character_create (CharacterCreate): The character object to create.

    Returns:
        Character: The created character object.
    """
    return db.create(Character(**character_create.dict()))


@router.get(
    "/characters", response_model=list[Character], response_model_exclude_defaults=True
)
def get_characters(request: Request) -> list[dict[str, Any]]:
    """Fetches a list of characters based on the provided parameters.

    Allows ordering by and selecting specific columns (meaning
    the resulting object may not contain all Character fields).

    Args:
        request (Request): The HTTP request containing query parameters.

    Returns:
        list[dict[str, Any]]: A list of (partial) character objects.
    """
    params = GetCharactersParams.from_request(request)
    return db.get(params)


@router.get("/characters/{character_id}")
def read_character(character_id: int) -> Character:
    """Fetches a character by their ID.

    Args:
        character_id (int): The ID of the character to fetch.

    Returns:
        Character: The character object corresponding to the given ID.
    """
    return db.get_by_id(character_id, Character)


@router.delete("/characters/{character_id}", status_code=HTTPStatus.ACCEPTED)
def delete_character(character_id: int) -> dict:
    """Deletes a character by their ID.

    Args:
        character_id (int): The ID of the character to delete.

    Returns:
        dict: Empty dictionary.
    """
    db.delete_by_id(character_id, Character)
    return {}


@router.get("/chat/history")
def get_chat_history(request: Request) -> list[Message]:
    """Fetches the chat history for a specific thread and character.

    Args:
        request (Request): The HTTP request containing thread_id and character_id.

    Returns:
        dict[str, list[dict[str, Any]]]: A dictionary containing the chat history data.
    """
    params = GetChatHistoryParams(**dict(request.query_params))
    agent = LlmWorkflow.from_thread_id(params.thread_id, params.character_id)
    chat_history = agent.get_state(params.thread_id).values.get("chat_history", [])

    return [
        Message(
            sender=Sender.user if isinstance(message, HumanMessage) else Sender.bot,
            text=message.content,
        )
        for message in chat_history
    ]


@router.get("/chats")
def get_chats(request: Request) -> list[int]:
    """Retrieves character IDs associated with a specific thread.

    Args:
        request (Request): The HTTP request containing query parameters for thread_id.

    Returns:
        dict[str, list[int]]: A dictionary containing the character IDs.
    """
    params = GetChatsParams(**dict(request.query_params))
    character_ids = LlmWorkflow.get_character_ids_from_thread_id(params.thread_id)

    return character_ids


@router.post("/chat/stream", status_code=HTTPStatus.ACCEPTED)
async def stream(
    query: str = Body(),
    character_id: int = Body(),
    thread_id: str = Body(),
) -> StreamingResponse:
    """Streams the LLM responses chunk by chunk as an event stream.

    Args:
        query (str): The input query from the user.
        character_id (int): The ID of the character participating in the chat.
        thread_id (str): The ID of the chat thread.

    Returns:
        StreamingResponse: An event stream that yields LLM responses as text chunks.
    """

    async def event_stream() -> AsyncGenerator[str, None]:
        """Internal function to stream LLM responses in real-time."""
        agent = LlmWorkflow.from_thread_id(thread_id, character_id)
        first, gathered = True, None
        last_msg_id, should_yield = None, False
        chat_history = agent.get_state(thread_id).values.get("chat_history")

        async for msg, metadata in agent.graph.astream(
            {"input": query},
            stream_mode="messages",
            config=agent.get_config(thread_id),
        ):
            # Filter out the summarization AIMessageChunk
            if chat_history:
                if last_msg_id and last_msg_id != msg.id:
                    should_yield = True
                last_msg_id = msg.id
            else:
                should_yield = True

            if isinstance(msg, AIMessageChunk):
                if first:
                    gathered = msg
                    first = False
                else:
                    gathered = gathered + msg

                if msg.content and should_yield:
                    yield msg.content

    return StreamingResponse(event_stream(), media_type="text/event-stream")

from http import HTTPStatus
from typing import Any, AsyncGenerator

from fastapi import APIRouter, Body, Request
from langchain_core.messages import AIMessageChunk, HumanMessage
from starlette.responses import StreamingResponse

from database.database import Database
from datamodels.enums import Sender
from datamodels.models import Character, GetCharactersParams, GetChatHistoryParams
from llm.llm_workflow import LlmWorkflow
from scraper.scraper import NarutoWikiScraper
from utils.logger import get_logger

router = APIRouter()
db = Database()
logger = get_logger()


@router.on_event("startup")
async def on_startup():
    scraper = NarutoWikiScraper()
    await scraper.scrape_all_characters()


@router.post("/characters/")
def create_character(character: Character) -> Character:
    return db.create(character)


@router.get("/characters")
def get_characters(request: Request) -> list[dict[str, Any]]:
    params = GetCharactersParams.from_request(request)
    return db.get(params)


@router.get("/characters/{character_id}")
def read_character(character_id: int) -> Character:
    return db.get_by_id(character_id, Character)


@router.delete("/characters/{character_id}")
def delete_character(character_id: int):
    db.delete_by_id(character_id, Character)
    return {"status": HTTPStatus.ACCEPTED}


@router.get("/chat/history")
def get_chat_history(request: Request) -> list[dict[str, Any]]:
    params = GetChatHistoryParams(**dict(request.query_params))
    agent = LlmWorkflow.from_thread_id(params.thread_id, params.character_id)
    chat_history = agent.get_state(params.thread_id).values.get("chat_history", [])

    return [
        {
            "sender": Sender.user if type(message) is HumanMessage else Sender.bot,
            "text": message.content,
        }
        for message in chat_history
    ]


@router.post("/chat/stream")
async def stream(
    query: str = Body(),
    character_id: int = Body(),
    thread_id: str = Body(),
) -> StreamingResponse:
    async def event_stream() -> AsyncGenerator[str, None]:
        """Function to stream LLM responses chunk by chunk."""
        agent = LlmWorkflow.from_thread_id(thread_id, character_id)
        first, gathered = True, None
        last_msg_id, should_yield = None, False
        chat_history = agent.get_state(thread_id).values.get("chat_history")

        async for msg, metadata in agent.graph.astream(
            {"input": query},
            stream_mode="messages",
            config=agent.get_config(thread_id),
        ):
            # This filters out the summarization AIMessageChunk
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

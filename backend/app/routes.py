import json
from http import HTTPStatus
from typing import Any, AsyncGenerator

from fastapi import APIRouter, Body, Request, WebSocket
from langchain_core.messages import AIMessageChunk, HumanMessage, ToolMessage
from starlette.responses import StreamingResponse

from app.llm_workflow import LlmWorkflow
from database.database import Database
from datamodels.models import Character, GetCharactersQueryParams
from scraper.scraper import NarutoWikiScraper

router = APIRouter()
db = Database()


@router.on_event("startup")
async def on_startup():
    scraper = NarutoWikiScraper()
    await scraper.scrape_all_characters()


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


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        message = json.loads(data)
        user_message = message.get("message")

        # Fictional character's response logic
        character_response = {
            "user": "FictionalCharacter",
            "message": f"I heard you say: {user_message}",
        }

        await websocket.send_text(json.dumps(character_response))


agents_store = {}


def get_agent(character_id: int, thread_id: str) -> LlmWorkflow:
    """Retrieve or create a conversational agent based on the thread_id."""
    if thread_id not in agents_store:
        print("creating agent")
        # Create a new agent if one doesn't exist for this thread
        agents_store[thread_id] = LlmWorkflow(character_id)
    return agents_store[thread_id]


async def event_stream(query: str, character_id: int, thread_id: str) -> AsyncGenerator[str, None]:
    """Function to stream LLM responses token by token."""
    agent = get_agent(character_id, thread_id)
    first, gathered = True, None
    last_msg_id, should_yield = None, False
    chat_history = agent.graph.get_state({"configurable": {"thread_id": thread_id}}).values.get("chat_history")
    print(thread_id, chat_history)
    # Stream the conversation response from the LLM
    async for msg, metadata in agent.graph.astream(
            {"input": query}, stream_mode="messages", config={"configurable": {"thread_id": thread_id}}
    ):
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


@router.post("/stream")
async def stream(query: str = Body(), character_id: int = Body(), thread_id: str = Body()) -> StreamingResponse:
    return StreamingResponse(
        event_stream(query, character_id, thread_id), media_type="text/event-stream"
    )

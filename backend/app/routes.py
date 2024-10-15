from http import HTTPStatus
from typing import Annotated, Any

from fastapi import APIRouter, Body, Request
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, ToolMessage

from app.llm_workflow import graph
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


def event_stream(query: str):
    initial_state = {"messages": [HumanMessage(content=query)]}
    print(initial_state)
    return
    for chunk in graph.stream(initial_state):
        for node_name, node_results in chunk.items():
            chunk_messages = node_results.get("messages", [])
            for message in chunk_messages:
                # You can have any logic you like here
                # The important part is the yield
                if not message.content:
                    continue
                if isinstance(message, ToolMessage):
                    event_str = "event: tool_event"
                else:
                    event_str = "event: ai_event"
                data_str = f"data: {message.content}"
                yield f"{event_str}\n{data_str}\n\n"


@router.post("/stream")
async def stream(query: Annotated[str, Body(embed=True)]):
    return StreamingResponse(event_stream(query), media_type="text/event-stream")

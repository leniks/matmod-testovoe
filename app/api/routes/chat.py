from __future__ import annotations

from typing import AsyncGenerator

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from app.dependencies import get_agent_service
from app.schemas.chat import ChatRequest, ChatResponse
from app.utils.sse import to_sse_data

router = APIRouter(prefix="/chat", tags=["chat"])


async def _stream_agent(message: str) -> AsyncGenerator[str, None]:
    agent_service = get_agent_service()
    async for event in agent_service.run_stream(message):
        yield to_sse_data(event)
    yield "event: done\ndata: {}\n\n"


@router.get("/stream")
async def chat_stream(message: str = Query(..., min_length=2)) -> StreamingResponse:
    return StreamingResponse(_stream_agent(message), media_type="text/event-stream")


@router.post("", response_model=ChatResponse)
async def chat(body: ChatRequest) -> ChatResponse:
    agent_service = get_agent_service()
    final = ""
    async for event in agent_service.run_stream(body.message):
        if event.get("type") == "final":
            final = str(event["message"])
    return ChatResponse(answer=final)

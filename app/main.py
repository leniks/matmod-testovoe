from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse

load_dotenv()
from app.api.routes.chat import router as chat_router

app = FastAPI(title="Track A Agent API")
app.include_router(chat_router)


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(Path("static/index.html"))

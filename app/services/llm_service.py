from __future__ import annotations

import asyncio
from typing import Any

from app.core.settings import Settings
from app.schemas.agent import AgentDecision
from app.utils.json_utils import extract_json_object


class LLMService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: Any | None = None
        self._init_client()

    @property
    def is_configured(self) -> bool:
        return self._client is not None

    def _init_client(self) -> None:
        if not self._settings.gigachat_credentials:
            return

        try:
            from langchain_gigachat.chat_models import GigaChat
        except ImportError:
            return

        kwargs: dict[str, Any] = {
            "credentials": self._settings.gigachat_credentials,
            "scope": self._settings.gigachat_scope,
            "verify_ssl_certs": self._settings.gigachat_verify_ssl_certs,
            "temperature": 0,
        }
        if self._settings.gigachat_model:
            kwargs["model"] = self._settings.gigachat_model
        self._client = GigaChat(**kwargs)

    async def _invoke(self, messages: list[tuple[str, str]]) -> str:
        if not self._client:
            return ""
        response = await asyncio.to_thread(self._client.invoke, messages)
        return (response.content or "").strip()

    async def decide_tool_usage(self, user_query: str) -> AgentDecision | None:
        if not self._client:
            return None

        prompt = (
            "Ты роутер инструментов. Верни СТРОГО JSON без markdown:\n"
            '{\n  "need_weather": boolean,\n  "need_fx": boolean,\n'
            '  "city": string,\n  "base": string,\n  "target": string,\n'
            '  "reason": string\n}\n'
            "Если поле неизвестно, верни пустую строку."
        )
        raw = await self._invoke([("system", prompt), ("human", user_query)])
        parsed = extract_json_object(raw)
        if not parsed:
            return None

        try:
            return AgentDecision.model_validate(parsed)
        except Exception:
            return None

    async def answer_without_tools(self, user_query: str) -> str | None:
        if not self._client:
            return None
        prompt = (
            "Ответь кратко и по делу на русском языке. "
            "Если вопрос требует актуальных данных из внешних источников, "
            "сделай аккуратное допущение и явно пометь это."
        )
        text = await self._invoke([("system", prompt), ("human", user_query)])
        return text or None

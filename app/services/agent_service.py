from __future__ import annotations

import re
from typing import Any, AsyncGenerator

from app.schemas.agent import AgentDecision
from app.services.external_data_service import ExternalDataService
from app.services.llm_service import LLMService


class AgentService:
    def __init__(self, llm_service: LLMService, external_data_service: ExternalDataService) -> None:
        self._llm_service = llm_service
        self._external_data_service = external_data_service

    async def _decide(self, user_query: str) -> AgentDecision:
        llm_decision = await self._llm_service.decide_tool_usage(user_query)
        if llm_decision:
            return llm_decision
        return self._rule_decide(user_query)

    def _rule_decide(self, user_query: str) -> AgentDecision:
        query = user_query.lower()
        need_weather = any(word in query for word in ["погод", "weather", "температур"])
        need_fx = any(word in query for word in ["курс", "доллар", "usd", "eur", "руб"])

        city = ""
        city_match = re.search(r"(?:в|во)\s+([а-яa-z\- ]{2,40}?)(?:\s+и|,|\?|$)", query)
        if city_match:
            city = city_match.group(1).strip().title()

        base = "EUR" if "eur" in query else "USD"
        target = "KZT" if "kzt" in query else "RUB"

        return AgentDecision(
            need_weather=need_weather,
            need_fx=need_fx,
            city=city or "Москва",
            base=base,
            target=target,
            reason="Решение принято эвристическим роутером.",
        )

    async def run_stream(self, user_query: str) -> AsyncGenerator[dict[str, Any], None]:
        decision = await self._decide(user_query)
        yield {"type": "thought", "message": decision.reason}

        weather_data: dict[str, Any] | None = None
        fx_data: dict[str, Any] | None = None
        used_tools = False

        if decision.need_weather:
            used_tools = True
            yield {
                "type": "tool_call",
                "tool": "get_weather",
                "args": {"city": decision.city or "Москва"},
            }
            try:
                weather_data = await self._external_data_service.get_weather(
                    decision.city or "Москва"
                )
            except Exception as exc:
                weather_data = {"ok": False, "error": f"Вызов weather API упал: {exc}"}
            yield {"type": "tool_result", "tool": "get_weather", "result": weather_data}

        if decision.need_fx:
            used_tools = True
            yield {
                "type": "tool_call",
                "tool": "get_fx_rate",
                "args": {"base": decision.base.upper(), "target": decision.target.upper()},
            }
            try:
                fx_data = await self._external_data_service.get_fx_rate(
                    decision.base, decision.target
                )
            except Exception as exc:
                fx_data = {"ok": False, "error": f"Вызов fx API упал: {exc}"}
            yield {"type": "tool_result", "tool": "get_fx_rate", "result": fx_data}

        if not used_tools:
            llm_answer = await self._llm_service.answer_without_tools(user_query)
            if llm_answer:
                yield {"type": "final", "message": llm_answer}
                return
            yield {
                "type": "final",
                "message": "LLM сейчас недоступна, уточни вопрос или попробуй позже.",
            }
            return

        final_parts: list[str] = []
        if weather_data:
            if weather_data.get("ok"):
                final_parts.append(
                    f"Погода: {weather_data['city']}, {weather_data['temperature_c']} °C, "
                    f"ветер {weather_data['wind_kmh']} км/ч."
                )
            else:
                final_parts.append(f"Погода: ошибка — {weather_data.get('error')}.")

        if fx_data:
            if fx_data.get("ok"):
                final_parts.append(
                    f"Курс: 1 {fx_data['base']} = {fx_data['rate']} {fx_data['target']} "
                    f"(дата {fx_data['date']})."
                )
            else:
                final_parts.append(f"Курс: ошибка — {fx_data.get('error')}.")

        yield {"type": "final", "message": " ".join(final_parts)}

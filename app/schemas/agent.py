from __future__ import annotations

from pydantic import BaseModel


class AgentDecision(BaseModel):
    need_weather: bool = False
    need_fx: bool = False
    city: str = ""
    base: str = "USD"
    target: str = "RUB"
    reason: str = "Решение принято эвристическим роутером."

from __future__ import annotations

from functools import lru_cache

from app.core.settings import get_settings
from app.services.agent_service import AgentService
from app.services.external_data_service import ExternalDataService
from app.services.llm_service import LLMService


@lru_cache
def get_agent_service() -> AgentService:
    settings = get_settings()
    llm_service = LLMService(settings)
    external_data_service = ExternalDataService()
    return AgentService(llm_service, external_data_service)

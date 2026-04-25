from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    gigachat_credentials: str
    gigachat_scope: str
    gigachat_model: str
    gigachat_verify_ssl_certs: bool


def get_settings() -> Settings:
    return Settings(
        gigachat_credentials=os.getenv("GIGACHAT_CREDENTIALS", "").strip(),
        gigachat_scope=os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS").strip(),
        gigachat_model=os.getenv("GIGACHAT_MODEL", "").strip(),
        gigachat_verify_ssl_certs=(
            os.getenv("GIGACHAT_VERIFY_SSL_CERTS", "true").strip().lower() != "false"
        ),
    )

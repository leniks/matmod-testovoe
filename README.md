Track: A

# AI-агент с инструментами API (погода + курс валют)

Мини-проект под трек A: агент получает запрос пользователя, решает нужно ли вызывать инструменты, вызывает внешние API и отвечает результатом.

## Что реализовано

- `tool #1`: погода через Open-Meteo API
- `tool #2`: курс валют через ExchangeRate API
- агентный роутер:
  - с LLM GigaChat (если есть `GIGACHAT_CREDENTIALS`)
  - с fallback-эвристикой (если ключа нет)
- SSE-стрим `thought -> tool_call -> tool_result -> final`
- простой веб-интерфейс с отображением шагов агента в реальном времени

## Запуск

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Открыть: `http://127.0.0.1:8000`

## API

- `GET /chat/stream?message=...` — SSE поток шагов агента
- `POST /chat` — обычный JSON-ответ

## Настройка GigaChat

1. Получите токен/ключ в кабинете GigaChat API.
2. Заполните `.env`:
   - `GIGACHAT_CREDENTIALS=...`
   - `GIGACHAT_SCOPE=GIGACHAT_API_PERS` (или ваш scope)
   - `GIGACHAT_MODEL=` (опционально)
   - `GIGACHAT_VERIFY_SSL_CERTS=true`
3. Если `GIGACHAT_CREDENTIALS` не указан, агент автоматически работает в fallback-режиме.

Пример запроса:
- `Какая погода в Казани и курс доллара к рублю?`

## Архитектура

- `app/api/routes/chat.py` — HTTP-ручки и SSE стриминг
- `app/services/agent_service.py` — оркестрация агентного сценария
- `app/services/llm_service.py` — интеграция с GigaChat
- `app/services/external_data_service.py` — интеграции с внешними API
- `app/schemas/` — pydantic-схемы запросов и внутренних структур
- `app/utils/` — вспомогательные утилиты (JSON/SSE)
- `app/core/settings.py` — конфигурация окружения
- `static/index.html` — фронт для live-таймлайна


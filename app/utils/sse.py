from __future__ import annotations

import json
from typing import Any


def to_sse_data(event: dict[str, Any]) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

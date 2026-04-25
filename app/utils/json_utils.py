from __future__ import annotations

import json
import re
from typing import Any


def extract_json_object(text: str) -> dict[str, Any] | None:
    payload = text.strip()
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", payload)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None

from __future__ import annotations

import json
from typing import Any, Dict, Tuple


def build_message_payload(
    message_type: str,
    content: str,
    sender: str | None,
    created_at: str | None = None,
    is_history: bool = False,
) -> Dict[str, Any]:
    return {
        "type": "message",
        "message_type": message_type,
        "from": sender,
        "content": content,
        "created_at": created_at,
        "history": is_history,
    }


def build_users_payload(users: list[dict]) -> Dict[str, Any]:
    return {"type": "users", "items": users}


def parse_incoming_message(raw_message: str) -> Tuple[str, str]:
    """Parse incoming WebSocket payload, fallback to plain text."""
    message_type = "text"
    content = raw_message

    if raw_message.startswith("{"):
        try:
            payload = json.loads(raw_message)
            if payload.get("type") == "message":
                message_type = payload.get("message_type") or "text"
                content = str(payload.get("content") or "")
        except json.JSONDecodeError:
            pass

    return message_type, content

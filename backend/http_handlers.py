from fastapi import APIRouter, Query

from backend.db import get_messages

router = APIRouter()


@router.get("/")
async def health_check() -> dict:
    return {"status": "ok"}


@router.get("/messages")
async def list_messages(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> dict:
    messages = await get_messages(limit=limit, offset=offset)
    return {"count": len(messages), "items": messages}

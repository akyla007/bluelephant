import asyncio
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path("messages.db")


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _get_conn()
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def _insert_message_sync(client_id: str, content: str) -> None:
    conn = _get_conn()
    try:
        conn.execute(
            "INSERT INTO messages (client_id, content) VALUES (?, ?);",
            (client_id, content),
        )
        conn.commit()
    finally:
        conn.close()


async def insert_message(client_id: str, content: str) -> None:
    await asyncio.to_thread(_insert_message_sync, client_id, content)


def _get_recent_messages_sync(limit: int = 20) -> List[Dict[str, Any]]:
    conn = _get_conn()
    try:
        rows = conn.execute(
            """
            SELECT id, client_id, content, created_at
            FROM messages
            ORDER BY id DESC
            LIMIT ?;
            """,
            (limit,),
        ).fetchall()
        # Retorna em ordem cronológica (do mais antigo para o mais novo)
        rows = list(reversed(rows))
        return [dict(r) for r in rows]
    finally:
        conn.close()


async def get_recent_messages(limit: int = 20) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(_get_recent_messages_sync, limit)

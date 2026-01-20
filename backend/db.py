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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                name TEXT PRIMARY KEY,
                last_seen TEXT NOT NULL DEFAULT (datetime('now')),
                is_online INTEGER NOT NULL DEFAULT 0
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


def _upsert_user_sync(name: str) -> None:
    conn = _get_conn()
    try:
        conn.execute(
            """
            INSERT INTO users (name, last_seen, is_online)
            VALUES (?, datetime('now'), 0)
            ON CONFLICT(name) DO UPDATE SET last_seen = datetime('now');
            """,
            (name,),
        )
        conn.commit()
    finally:
        conn.close()


def _set_user_online_sync(name: str, is_online: bool) -> None:
    conn = _get_conn()
    try:
        conn.execute(
            """
            UPDATE users
            SET is_online = ?, last_seen = datetime('now')
            WHERE name = ?;
            """,
            (1 if is_online else 0, name),
        )
        conn.commit()
    finally:
        conn.close()


def _get_all_users_sync() -> List[Dict[str, Any]]:
    conn = _get_conn()
    try:
        rows = conn.execute(
            """
            SELECT name, last_seen, is_online
            FROM users
            ORDER BY is_online DESC, name ASC;
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


async def upsert_user(name: str) -> None:
    await asyncio.to_thread(_upsert_user_sync, name)


async def set_user_online(name: str, is_online: bool) -> None:
    await asyncio.to_thread(_set_user_online_sync, name, is_online)


async def get_all_users() -> List[Dict[str, Any]]:
    return await asyncio.to_thread(_get_all_users_sync)


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


def _get_messages_sync(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    conn = _get_conn()
    try:
        rows = conn.execute(
            """
            SELECT id, client_id, content, created_at
            FROM messages
            ORDER BY id DESC
            LIMIT ? OFFSET ?;
            """,
            (limit, offset),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


async def get_messages(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(_get_messages_sync, limit, offset)


async def get_recent_messages(limit: int = 20) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(_get_recent_messages_sync, limit)

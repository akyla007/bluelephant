import json
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.chat_protocol import build_message_payload, parse_incoming_message
from backend.connection_manager import ConnectionManager
from backend.db import (
    get_all_users,
    get_recent_messages,
    insert_message,
    set_user_online,
    upsert_user,
)


def get_websocket_router(manager: ConnectionManager) -> APIRouter:
    router = APIRouter()

    async def broadcast_chat_message(
        message_type: str,
        content: str,
        sender: str | None,
        created_at: str | None = None,
        is_history: bool = False,
    ) -> None:
        await manager.broadcast_json(
            build_message_payload(
                message_type,
                content,
                sender,
                created_at=created_at,
                is_history=is_history,
            )
        )

    @router.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        fallback_id = str(uuid.uuid4())[:8]  # curto e legível
        requested_name = (websocket.query_params.get("name") or "").strip()
        client_name = requested_name or f"anon-{fallback_id}"
        await manager.connect(websocket, client_name)
        await upsert_user(client_name)
        await set_user_online(client_name, True)

        # Histórico inicial (limite 20)
        history = await get_recent_messages(limit=20)
        for msg in history:
            await websocket.send_text(
                json.dumps(
                    build_message_payload(
                        msg.get("message_type", "text"),
                        msg["content"],
                        msg["client_id"],
                        created_at=msg["created_at"],
                        is_history=True,
                    )
                )
            )

        # Aviso de entrada (opcional)
        await broadcast_chat_message("system", f"{client_name} entrou no chat", None)
        await manager.broadcast_users(await get_all_users())

        try:
            while True:
                raw_message = await websocket.receive_text()
                message_type, content = parse_incoming_message(raw_message)

                # 1) salva no banco
                await insert_message(
                    client_id=client_name,
                    content=content,
                    message_type=message_type,
                )

                # 2) faz broadcast
                await broadcast_chat_message(message_type, content, client_name)

        except WebSocketDisconnect:
            manager.disconnect(websocket)
            await broadcast_chat_message("system", f"{client_name} saiu do chat", None)
            if not manager.has_name_active(client_name):
                await set_user_online(client_name, False)
            await manager.broadcast_users(await get_all_users())

    return router

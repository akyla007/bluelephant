import json
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

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
            {
                "type": "message",
                "message_type": message_type,
                "from": sender,
                "content": content,
                "created_at": created_at,
                "history": is_history,
            }
        )

    @router.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        fallback_id = str(uuid.uuid4())[:8]  # curto e legível
        requested_name = (websocket.query_params.get("name") or "").strip()
        client_name = requested_name or f"anon-{fallback_id}"
        await manager.connect(websocket, client_name)
        await upsert_user(client_name)
        await set_user_online(client_name, True)

        # (Opcional) Envia histórico ao conectar
        history = await get_recent_messages(limit=20)
        for msg in history:
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "message",
                        "message_type": msg.get("message_type", "text"),
                        "from": msg["client_id"],
                        "content": msg["content"],
                        "created_at": msg["created_at"],
                        "history": True,
                    }
                )
            )

        # Aviso de entrada (opcional)
        await broadcast_chat_message("system", f"{client_name} entrou no chat", None)
        await manager.broadcast_users(await get_all_users())

        try:
            while True:
                raw_message = await websocket.receive_text()

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

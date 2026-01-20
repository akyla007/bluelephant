import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.connection_manager import ConnectionManager
from backend.db import get_recent_messages, insert_message


def get_websocket_router(manager: ConnectionManager) -> APIRouter:
    router = APIRouter()

    @router.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        fallback_id = str(uuid.uuid4())[:8]  # curto e legível
        requested_name = (websocket.query_params.get("name") or "").strip()
        client_name = requested_name or f"anon-{fallback_id}"
        await manager.connect(websocket, client_name)

        # (Opcional) Envia histórico ao conectar
        history = await get_recent_messages(limit=20)
        for msg in history:
            await websocket.send_text(
                f"[history:{msg['created_at']}] {msg['client_id']}: {msg['content']}"
            )

        # Aviso de entrada (opcional)
        await manager.broadcast(f"[system] {client_name} entrou no chat")
        await manager.broadcast_users()

        try:
            while True:
                content = await websocket.receive_text()

                # 1) salva no banco
                await insert_message(client_id=client_name, content=content)

                # 2) faz broadcast
                await manager.broadcast(f"{client_name}: {content}")

        except WebSocketDisconnect:
            manager.disconnect(websocket)
            await manager.broadcast(f"[system] {client_name} saiu do chat")
            await manager.broadcast_users()

    return router

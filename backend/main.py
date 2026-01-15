import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from backend.connection_manager import ConnectionManager
from backend.db import get_recent_messages, init_db, insert_message

app = FastAPI()
manager = ConnectionManager()


@app.on_event("startup")
async def startup() -> None:
    init_db()


@app.get("/")
async def health_check() -> dict:
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    client_id = str(uuid.uuid4())[:8]  # curto e legível
    await manager.connect(websocket)

    # (Opcional) Envia histórico ao conectar
    history = await get_recent_messages(limit=20)
    for msg in history:
        await websocket.send_text(
            f"[history:{msg['created_at']}] {msg['client_id']}: {msg['content']}"
        )

    # Aviso de entrada (opcional)
    await manager.broadcast(f"[system] {client_id} entrou no chat")

    try:
        while True:
            content = await websocket.receive_text()

            # 1) salva no banco
            await insert_message(client_id=client_id, content=content)

            # 2) faz broadcast
            await manager.broadcast(f"{client_id}: {content}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"[system] {client_id} saiu do chat")

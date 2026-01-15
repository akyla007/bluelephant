from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from backend.connection_manager import ConnectionManager

app = FastAPI()
manager = ConnectionManager()


@app.get("/")
async def health_check() -> dict:
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)

    try:
        while True:
            message = await websocket.receive_text()
            await manager.broadcast(message)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

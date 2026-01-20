import json
from typing import Dict, List

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, client_name: str) -> None:
        await websocket.accept()
        self.active_connections[websocket] = client_name

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.pop(websocket, None)

    async def broadcast(self, message: str) -> None:
        for connection in list(self.active_connections.keys()):
            await connection.send_text(message)

    def get_user_names(self) -> List[str]:
        return list(self.active_connections.values())

    async def broadcast_users(self) -> None:
        payload = json.dumps({"type": "users", "items": self.get_user_names()})
        for connection in list(self.active_connections.keys()):
            await connection.send_text(payload)

import json
from typing import Dict, List

from fastapi import WebSocket

from backend.chat_protocol import build_users_payload


class ConnectionManager:
    def __init__(self) -> None:
        # websocket -> nome do usuário
        self.active_connections: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, client_name: str) -> None:
        await websocket.accept()
        self.active_connections[websocket] = client_name

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.pop(websocket, None)

    async def broadcast(self, message: str) -> None:
        for connection in list(self.active_connections.keys()):
            await connection.send_text(message)

    async def broadcast_json(self, payload: dict) -> None:
        message = json.dumps(payload)
        for connection in list(self.active_connections.keys()):
            await connection.send_text(message)

    def get_user_names(self) -> List[str]:
        return list(self.active_connections.values())

    def has_name_active(self, name: str) -> bool:
        return any(
            active_name == name for active_name in self.active_connections.values()
        )

    async def broadcast_users(self, users: List[dict]) -> None:
        await self.broadcast_json(build_users_payload(users))

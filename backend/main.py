from fastapi import FastAPI

from backend.connection_manager import ConnectionManager
from backend.db import init_db
from backend.http_handlers import router as http_router
from backend.websocket_handlers import get_websocket_router

app = FastAPI()
manager = ConnectionManager()
app.include_router(http_router)
app.include_router(get_websocket_router(manager))


@app.on_event("startup")
async def startup() -> None:
    init_db()

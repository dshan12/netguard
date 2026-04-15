from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List, Dict
import json
import asyncio
import redis.asyncio as redis
from config import get_settings

router = APIRouter(prefix="/ws", tags=["websocket"])

settings = get_settings()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.redis_client: redis.Redis = None
        self.pubsub = None
        self._listener_task = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        if self.redis_client is None:
            await self._start_redis_listener()

    async def _start_redis_listener(self):
        self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)
        self.pubsub = self.redis_client.pubsub()
        await self.pubsub.subscribe("packets", "alerts")
        self._listener_task = asyncio.create_task(self._listen())

    async def _listen(self):
        async for message in self.pubsub.listen():
            if message["type"] == "message":
                await self.broadcast(message["data"])

    async def broadcast(self, message: str):
        for connection in self.active_connections.copy():
            try:
                await connection.send_text(message)
            except Exception:
                self.active_connections.remove(connection)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        if not self.active_connections and self._listener_task:
            self._listener_task.cancel()
            await self.pubsub.unsubscribe("packets", "alerts")
            await self.pubsub.close()
            await self.redis_client.close()
            self.redis_client = None
            self.pubsub = None
            self._listener_task = None


manager = ConnectionManager()


@router.websocket("/live")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
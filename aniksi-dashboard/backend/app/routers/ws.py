"""
WebSocket endpoint: subscribes to Redis pub/sub and streams dashboard updates
to all connected browser clients.
"""
import asyncio
import json
import logging
import redis.asyncio as aioredis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.config import settings

router = APIRouter(tags=["websocket"])
log = logging.getLogger(__name__)


@router.websocket("/ws/dashboard")
async def ws_dashboard(websocket: WebSocket):
    await websocket.accept()
    r = aioredis.from_url(settings.redis_url, decode_responses=True)
    pubsub = r.pubsub()
    await pubsub.subscribe("dashboard:updates")
    log.info("WebSocket client connected")

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                await websocket.send_text(message["data"])
    except WebSocketDisconnect:
        log.info("WebSocket client disconnected")
    except asyncio.CancelledError:
        pass
    finally:
        await pubsub.unsubscribe("dashboard:updates")
        await r.aclose()

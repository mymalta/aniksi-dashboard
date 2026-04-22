"""
Background task: runs the decision engine every engine_interval seconds,
pushes updates to all connected WebSocket clients via Redis pub/sub.
"""
import asyncio
import logging
from datetime import datetime, timezone

from app.config import settings
from app.db.database import AsyncSessionLocal
from app.db.redis import redis_publish
from app.services.state import build_live_overview

log = logging.getLogger(__name__)


async def run_engine_loop():
    log.info("Engine loop started (interval=%ds)", settings.engine_interval)
    while True:
        try:
            async with AsyncSessionLocal() as db:
                now = datetime.now(timezone.utc)
                overview = await build_live_overview(db, now)
                await redis_publish("dashboard:updates", overview.model_dump(mode="json"))
                log.debug("Engine tick: status=%s pressure=%.2f", overview.status, overview.global_pressure)
        except Exception:
            log.exception("Engine loop error")
        await asyncio.sleep(settings.engine_interval)

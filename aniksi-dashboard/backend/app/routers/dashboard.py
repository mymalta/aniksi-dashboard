from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.db.redis import redis_get
from app.models.agent import ShiftSnapshot, RoleOverride, PlannedRole
from app.schemas.dashboard import (
    LiveOverview, TimeseriesResponse, TimeseriesPoint,
    ManualOverrideRequest, ManualOverrideResponse,
)
from app.services.state import build_live_overview

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/live", response_model=LiveOverview)
async def get_live(db: AsyncSession = Depends(get_db)):
    cached = await redis_get("dashboard:live")
    if cached:
        return LiveOverview(**cached)
    now = datetime.now(timezone.utc)
    return await build_live_overview(db, now)


@router.get("/timeseries", response_model=TimeseriesResponse)
async def get_timeseries(window: str = "24h", db: AsyncSession = Depends(get_db)):
    window_hours = {"1h": 1, "6h": 6, "24h": 24, "7d": 168}.get(window, 24)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)

    result = await db.execute(
        select(ShiftSnapshot)
        .where(ShiftSnapshot.timestamp >= cutoff)
        .order_by(ShiftSnapshot.timestamp.asc())
    )
    snapshots = result.scalars().all()

    points = [
        TimeseriesPoint(
            timestamp=s.timestamp,
            chat_pressure=s.active_chat_pressure,
            ticket_pressure=s.ticket_pressure,
            global_pressure=s.global_pressure,
            scheduled_agents=s.scheduled_agents,
            online_agents=s.online_agents,
            recommended_action=s.recommended_action,
        )
        for s in snapshots
    ]
    return TimeseriesResponse(window=window, points=points)


@router.post("/manual-role-override", response_model=ManualOverrideResponse)
async def manual_role_override(
    body: ManualOverrideRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        new_role = PlannedRole(body.new_role)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid role: {body.new_role}")

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=body.duration_minutes)

    # Deactivate any existing override for this agent
    existing = await db.execute(
        select(RoleOverride).where(
            RoleOverride.agent_id == body.agent_id,
            RoleOverride.active == True,
        )
    )
    for override in existing.scalars().all():
        override.active = False

    override = RoleOverride(
        agent_id=body.agent_id,
        new_role=new_role,
        reason=body.reason,
        override_by=body.override_by,
        created_at=now,
        expires_at=expires_at,
        active=True,
    )
    db.add(override)
    await db.commit()

    return ManualOverrideResponse(
        success=True,
        agent_id=body.agent_id,
        new_role=new_role.value,
        expires_at=expires_at,
    )

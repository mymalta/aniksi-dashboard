from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.agent import AgentBoardResponse
from app.services.state import build_agent_states

router = APIRouter(prefix="/dashboard", tags=["agents"])


@router.get("/agents", response_model=AgentBoardResponse)
async def get_agents(db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc)
    states = await build_agent_states(db, now)
    return AgentBoardResponse(generated_at=now, agents=states)

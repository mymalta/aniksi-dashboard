from datetime import datetime
from pydantic import BaseModel
from app.models.agent import PlannedRole, AlertState


class LiveAgentState(BaseModel):
    agent_id: str
    agent_name: str
    scheduled: bool
    shift_start: datetime
    shift_end: datetime
    planned_role: PlannedRole
    current_role: PlannedRole
    presence_status: str
    presence_stale: bool              # True if last_seen_at > 3 min ago
    absence_seconds: int              # seconds offline; 0 if online
    active_chats_estimated: int
    chats_unowned: bool               # True if agent is in absence grace window
    assigned_open_tickets: int
    overdue_assigned_tickets: int
    workload_score: float
    utilization_score: float
    alert_state: AlertState
    recommendation: str               # stay / help_chat / help_ticket / take_break / overloaded


class AgentBoardResponse(BaseModel):
    generated_at: datetime
    agents: list[LiveAgentState]

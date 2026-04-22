from datetime import datetime
from pydantic import BaseModel


class Recommendation(BaseModel):
    action: str
    agent_id: str
    agent_name: str
    from_role: str
    to_role: str
    confidence: float
    reason: str


class LiveOverview(BaseModel):
    generated_at: datetime
    scheduled_agents: int
    online_agents: int
    agents_on_break: int
    active_chats: int
    queued_chats: int
    open_tickets: int
    unassigned_tickets: int
    overdue_tickets: int
    avg_chat_wait_seconds: float
    chat_pressure: float
    ticket_pressure: float
    global_pressure: float
    status: str                       # green / amber / red
    recommendations: list[Recommendation]


class TimeseriesPoint(BaseModel):
    timestamp: datetime
    chat_pressure: float
    ticket_pressure: float
    global_pressure: float
    scheduled_agents: int
    online_agents: int
    recommended_action: str | None


class TimeseriesResponse(BaseModel):
    window: str
    points: list[TimeseriesPoint]


class ManualOverrideRequest(BaseModel):
    agent_id: str
    new_role: str
    reason: str
    override_by: str | None = None
    duration_minutes: int = 60


class ManualOverrideResponse(BaseModel):
    success: bool
    agent_id: str
    new_role: str
    expires_at: datetime

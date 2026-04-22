from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, Float, Integer, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum
from app.db.database import Base


class PlannedRole(str, enum.Enum):
    chat_core = "chat_core"
    ticket_core = "ticket_core"
    flex = "flex"
    off = "off"


class PresenceStatus(str, enum.Enum):
    online = "online"
    away = "away"
    busy = "busy"
    offline = "offline"
    break_ = "break"
    unknown = "unknown"


class AlertState(str, enum.Enum):
    ok = "ok"
    warning = "warning"
    critical = "critical"
    overloaded = "overloaded"


class AgentSchedule(Base):
    __tablename__ = "agent_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_id: Mapped[str] = mapped_column(String, index=True)
    agent_name: Mapped[str] = mapped_column(String)
    shift_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    shift_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    shift_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    break_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    break_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    planned_role: Mapped[PlannedRole] = mapped_column(SAEnum(PlannedRole))
    shared_account: Mapped[str | None] = mapped_column(String, nullable=True)
    team: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class RoleOverride(Base):
    __tablename__ = "role_overrides"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_id: Mapped[str] = mapped_column(String, index=True)
    new_role: Mapped[PlannedRole] = mapped_column(SAEnum(PlannedRole))
    reason: Mapped[str] = mapped_column(String)
    override_by: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class ShiftSnapshot(Base):
    __tablename__ = "shift_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    scheduled_agents: Mapped[int] = mapped_column(Integer)
    online_agents: Mapped[int] = mapped_column(Integer)
    chat_core_agents: Mapped[int] = mapped_column(Integer)
    ticket_core_agents: Mapped[int] = mapped_column(Integer)
    flex_agents: Mapped[int] = mapped_column(Integer)
    active_chat_pressure: Mapped[float] = mapped_column(Float)
    ticket_pressure: Mapped[float] = mapped_column(Float)
    global_pressure: Mapped[float] = mapped_column(Float)
    recommended_action: Mapped[str | None] = mapped_column(String, nullable=True)

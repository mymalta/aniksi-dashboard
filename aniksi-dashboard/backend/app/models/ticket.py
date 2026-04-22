from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum
from app.db.database import Base


class TicketStatus(str, enum.Enum):
    open = "open"
    pending = "pending"
    solved = "solved"
    closed = "closed"


class TicketPriority(str, enum.Enum):
    low = "low"
    normal = "normal"
    high = "high"
    urgent = "urgent"


class TicketEvent(Base):
    __tablename__ = "ticket_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_id: Mapped[str] = mapped_column(String, index=True)
    source: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[TicketStatus] = mapped_column(SAEnum(TicketStatus))
    assigned_agent_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    assigned_agent_name: Mapped[str | None] = mapped_column(String, nullable=True)
    priority: Mapped[TicketPriority] = mapped_column(SAEnum(TicketPriority), default=TicketPriority.normal)
    queue: Mapped[str | None] = mapped_column(String, nullable=True)
    public_reply_count: Mapped[int] = mapped_column(Integer, default=0)
    first_response_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

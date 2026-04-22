from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Float, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum
from app.db.database import Base


class ChatStatus(str, enum.Enum):
    queued = "queued"
    active = "active"
    closed = "closed"


class ChatEvent(Base):
    __tablename__ = "chat_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_id: Mapped[str] = mapped_column(String, index=True)
    queue: Mapped[str | None] = mapped_column(String, nullable=True)
    shared_account: Mapped[str] = mapped_column(String, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[ChatStatus] = mapped_column(SAEnum(ChatStatus))
    wait_time_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    handle_time_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    language: Mapped[str | None] = mapped_column(String, nullable=True)
    # Derived at ingest time from schedule
    attributed_agent_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    # Coverage substitution flag
    is_substitution: Mapped[bool] = mapped_column(default=False)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

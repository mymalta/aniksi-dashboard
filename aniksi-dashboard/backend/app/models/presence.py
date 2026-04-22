from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum
from app.db.database import Base


class CurrentTool(str, enum.Enum):
    chat = "chat"
    ticket = "ticket"
    idle = "idle"


class PresenceEvent(Base):
    __tablename__ = "presence_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_id: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[str] = mapped_column(String)   # online/away/busy/offline/break/unknown
    current_tool: Mapped[str | None] = mapped_column(String, nullable=True)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)

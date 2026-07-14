from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class HCPInteraction(Base):
    __tablename__ = "hcp_interactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    hcp_name: Mapped[str] = mapped_column(String(160), index=True)
    interaction_type: Mapped[str] = mapped_column(String(80), default="Meeting")
    interaction_date: Mapped[date] = mapped_column(Date)
    interaction_time: Mapped[time] = mapped_column(Time)
    attendees: Mapped[str] = mapped_column(Text, default="")
    topics_discussed: Mapped[str] = mapped_column(Text, default="")
    materials_shared: Mapped[str] = mapped_column(Text, default="")
    samples_distributed: Mapped[str] = mapped_column(Text, default="")
    sentiment: Mapped[str] = mapped_column(String(24), default="Neutral")
    outcomes: Mapped[str] = mapped_column(Text, default="")
    follow_up_actions: Mapped[str] = mapped_column(Text, default="")
    ai_summary: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

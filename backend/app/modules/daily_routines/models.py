"""Daily routine / planner event entity model."""
import uuid
from datetime import date, datetime, time
from sqlalchemy import String, DateTime, Date, Time, Text, Integer, ForeignKey, Index, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class RoutineType(str):
    COMMUTE = "commute"
    EXERCISE = "exercise"
    OUTDOOR_WORK = "outdoor_work"
    INDOOR_AIR = "indoor_air"
    ENERGY = "energy"
    WASTE = "waste"
    OTHER = "other"


class RoutineStatus(str):
    PLANNED = "planned"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class DailyRoutineModel(Base):
    __tablename__ = "daily_routines"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    routine_type: Mapped[str] = mapped_column(String(30), nullable=False)
    routine_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    days_of_week: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=list, nullable=False)
    location_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("locations.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="planned", nullable=False)
    reminder_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_recommendation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("recommendations.id", ondelete="SET NULL"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_daily_routines_user_active", "user_id", "is_active"),
        Index("ix_daily_routines_user_date", "user_id", "routine_date"),
    )
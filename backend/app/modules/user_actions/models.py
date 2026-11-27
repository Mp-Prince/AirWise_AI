"""User action entity model."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Enum as SQLEnum, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base

class ActionType(str):
    ACCEPTED_RECOMMENDATION = "accepted_recommendation"
    DISMISSED_RECOMMENDATION = "dismissed_recommendation"
    COMPLETED_ROUTINE = "completed_routine"
    ADDED_LOCATION = "added_location"
    UPDATED_PROFILE = "updated_profile"

class UserActionModel(Base):
    __tablename__ = "user_actions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    action_type: Mapped[str] = mapped_column(String(30), nullable=False)
    reference_id: Mapped[uuid.UUID] = mapped_column(nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    __table_args__ = (
        Index("ix_user_actions_user_created", "user_id", "created_at"),
    )
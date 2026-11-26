"""User profile entity model."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, ForeignKey, Enum as SQLEnum, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class UserProfileModel(Base):
    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    gender: Mapped[str] = mapped_column(String(20), nullable=True)
    height_cm: Mapped[int] = mapped_column(nullable=True)
    weight_kg: Mapped[float] = mapped_column(nullable=True)
    health_conditions: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    sensitivities: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    preferred_units: Mapped[str] = mapped_column(String(20), default="metric", nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="profile")
"""Emission factor entity model."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base

class EmissionFactorModel(Base):
    __tablename__ = "emission_factors"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    activity: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    co2e_kg_per_unit: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    source: Mapped[str] = mapped_column(String(200), nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=True)
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_to: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_emission_factors_activity_region", "activity", "region"),
    )
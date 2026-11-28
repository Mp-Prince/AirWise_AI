"""Impact record entity model."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Numeric, ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class ImpactRecordModel(Base):
    __tablename__ = "impact_records"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    action_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("user_actions.id", ondelete="SET NULL"), nullable=True)
    emission_factor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("emission_factors.id", ondelete="SET NULL"), nullable=True)
    co2e_kg: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    baseline_co2e_kg: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    alternative_co2e_kg: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    method_version: Mapped[str] = mapped_column(String(40), default="airwise_transport_v1", nullable=False)
    factor_snapshot: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    is_estimated: Mapped[bool] = mapped_column(default=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_impact_records_user_recorded", "user_id", "recorded_at"),
    )
"""Weather reading entity model."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Numeric, ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base

class WeatherReadingModel(Base):
    __tablename__ = "weather_readings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    location_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    temperature_c: Mapped[float] = mapped_column(Numeric(4, 1), nullable=True)
    humidity_pct: Mapped[int] = mapped_column(nullable=True)
    pressure_hpa: Mapped[float] = mapped_column(Numeric(6, 1), nullable=True)
    wind_speed_ms: Mapped[float] = mapped_column(Numeric(4, 1), nullable=True)
    wind_direction_deg: Mapped[int] = mapped_column(nullable=True)
    precipitation_mm: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    uv_index: Mapped[float] = mapped_column(Numeric(3, 1), nullable=True)
    cloud_cover_pct: Mapped[int] = mapped_column(nullable=True)
    visibility_km: Mapped[float] = mapped_column(Numeric(4, 1), nullable=True)
    weather_code: Mapped[int] = mapped_column(nullable=True)
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    is_estimated: Mapped[bool] = mapped_column(default=False, nullable=False)
    raw_payload: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_weather_location_measured", "location_id", "measured_at"),
        Index("ix_weather_provider_measured", "provider", "measured_at"),
    )
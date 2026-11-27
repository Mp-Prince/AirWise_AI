"""Air quality reading entity model."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Numeric, ForeignKey, Enum as SQLEnum, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base

class AQIStandard(str):
    CPCB_INDIA = "CPCB_India"
    US_AQI = "US_AQI"

class AirQualityReadingModel(Base):
    __tablename__ = "air_quality_readings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    location_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    aqi_value: Mapped[int] = mapped_column(nullable=False)
    aqi_standard: Mapped[str] = mapped_column(String(20), default="US_AQI", nullable=False)
    pm25: Mapped[float] = mapped_column(Numeric(6, 2), nullable=True)
    pm10: Mapped[float] = mapped_column(Numeric(6, 2), nullable=True)
    o3: Mapped[float] = mapped_column(Numeric(6, 2), nullable=True)
    no2: Mapped[float] = mapped_column(Numeric(6, 2), nullable=True)
    so2: Mapped[float] = mapped_column(Numeric(6, 2), nullable=True)
    co: Mapped[float] = mapped_column(Numeric(6, 2), nullable=True)
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    is_estimated: Mapped[bool] = mapped_column(default=False, nullable=False)
    raw_payload: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_air_quality_location_measured", "location_id", "measured_at"),
        Index("ix_air_quality_provider_measured", "provider", "measured_at"),
    )
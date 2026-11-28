"""AI Assistant Pydantic schemas (Phase 5)."""
from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.rag.schema import RAGCitation


class AssistantChatRequest(BaseModel):
    conversation_id: Optional[UUID] = None
    message: str = Field(..., min_length=1, max_length=2000)
    include_user_context: bool = Field(default=True)


class StructuredRecommendation(BaseModel):
    title: str = Field(..., min_length=1, max_length=180)
    category: Literal["health", "commute", "indoor_air", "energy", "planning", "general"] = "general"
    priority: Literal["low", "medium", "high"] = "medium"
    action: str = Field(..., min_length=1, max_length=500)
    why: str = Field(..., min_length=1, max_length=500)
    expected_benefit: Optional[str] = Field(None, max_length=300)


class LLMGeneratedPayload(BaseModel):
    """Validated JSON structure expected from the LLM."""

    answer: str = Field(..., min_length=1)
    recommendations: list[StructuredRecommendation] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class AssistantDataContext(BaseModel):
    location: Optional[str] = None
    aqi_value: Optional[int] = None
    aqi_standard: Optional[str] = None
    aqi_category: Optional[str] = None
    air_quality_observed_at: Optional[datetime] = None
    weather_summary: Optional[str] = None
    weather_observed_at: Optional[datetime] = None
    user_sensitivities: list[str] = Field(default_factory=list)
    user_health_conditions: list[str] = Field(default_factory=list)


class AssistantUsageSummary(BaseModel):
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    calls_in_window: int = 0
    rate_limit_per_minute: int = 20
    estimated_cost_usd: float = 0.0


class AssistantChatResponse(BaseModel):
    conversation_id: UUID
    message_id: UUID
    answer: str
    recommendations: list[StructuredRecommendation] = Field(default_factory=list)
    sources: list[RAGCitation] = Field(default_factory=list)
    data_context: AssistantDataContext
    limitations: list[str] = Field(default_factory=list)
    usage: AssistantUsageSummary
    is_grounded: bool


class AssistantFeedbackRequest(BaseModel):
    message_id: UUID
    helpful: bool
    comment: Optional[str] = Field(None, max_length=500)


class AssistantFeedbackResponse(BaseModel):
    status: str
    message_id: UUID

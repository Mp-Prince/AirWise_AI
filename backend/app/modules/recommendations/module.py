"""Recommendations API module (Phase 6)."""
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_async_session
from app.modules.recommendations.models import RecommendationStatus
from app.modules.recommendations.schema import (
    AddToPlannerRequest,
    RecommendationListResponse,
    RecommendationResponse,
)
from app.modules.recommendations.service import RecommendationService
from app.modules.users.models import UserModel
from app.modules.users.routes import get_current_active_user

router = APIRouter(tags=["recommendations"])


@router.get("", response_model=RecommendationListResponse)
async def list_recommendations(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    category: Optional[str] = Query(None, description="Filter by category: health, lifestyle, eco"),
    rec_status: Optional[str] = Query(None, alias="status", description="Filter by status"),
):
    """List personalized recommendations for the signed-in user."""
    service = RecommendationService(session)
    res = await service.list_recommendations(
        user_id=current_user.id,
        category=category,
        status=rec_status,
    )
    await session.commit()
    return res


@router.get("/today", response_model=RecommendationListResponse)
async def get_today_recommendations(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Get pending recommendations for today (Dashboard summary)."""
    service = RecommendationService(session)
    res = await service.get_today(current_user.id)
    await session.commit()
    return res


@router.post("/generate", response_model=list[RecommendationResponse], status_code=status.HTTP_201_CREATED)
async def generate_recommendations(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Run deterministic rules + context to generate fresh recommendations."""
    service = RecommendationService(session)
    created = await service.generate_for_user(current_user.id)
    await session.commit()
    return created


@router.patch("/{rec_id}/accept", response_model=RecommendationResponse)
async def accept_recommendation(
    rec_id: UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Accept / mark done a recommendation."""
    service = RecommendationService(session)
    updated = await service.update_status(rec_id, current_user.id, RecommendationStatus.ACCEPTED)
    if not updated:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    await session.commit()
    return updated


@router.patch("/{rec_id}/dismiss", response_model=RecommendationResponse)
async def dismiss_recommendation(
    rec_id: UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Dismiss a recommendation."""
    service = RecommendationService(session)
    updated = await service.update_status(rec_id, current_user.id, RecommendationStatus.DISMISSED)
    if not updated:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    await session.commit()
    return updated


@router.post("/{rec_id}/add-to-planner")
async def add_recommendation_to_planner(
    rec_id: UUID,
    payload: AddToPlannerRequest,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Create a Daily Planner event from a recommendation and mark it accepted."""
    service = RecommendationService(session)
    try:
        result = await service.add_to_planner(rec_id, current_user.id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    if not result:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    await session.commit()
    return result

"""Daily routine / planner API module (Phase 6)."""
from datetime import date
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_async_session
from app.modules.daily_routines.schema import (
    DailyRoutineCreate,
    DailyRoutineListResponse,
    DailyRoutineResponse,
    DailyRoutineStatusUpdate,
    DailyRoutineUpdate,
)
from app.modules.daily_routines.service import DailyRoutineService
from app.modules.users.models import UserModel
from app.modules.users.routes import get_current_active_user

router = APIRouter(tags=["daily-routines"])


@router.get("", response_model=DailyRoutineListResponse)
async def list_routines(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    date_param: Optional[date] = Query(None, alias="date", description="Single date (YYYY-MM-DD)"),
    date_from: Optional[date] = Query(None, alias="from", description="Start date"),
    date_to: Optional[date] = Query(None, alias="to", description="End date"),
    routine_type: Optional[str] = Query(None, alias="category", description="Filter by category"),
    routine_status: Optional[str] = Query(None, alias="status", description="Filter by status"),
):
    """List scheduled planner events and routines for the user."""
    effective_from = date_param or date_from
    effective_to = date_param or date_to
    service = DailyRoutineService(session)
    return await service.list_routines(
        user_id=current_user.id,
        date_from=effective_from,
        date_to=effective_to,
        routine_type=routine_type,
        status=routine_status,
    )


@router.post("", response_model=DailyRoutineResponse, status_code=status.HTTP_201_CREATED)
async def create_routine(
    data: DailyRoutineCreate,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Create a new planner event or routine."""
    service = DailyRoutineService(session)
    created = await service.create_routine(current_user.id, data)
    await session.commit()
    return created


@router.put("/{routine_id}", response_model=DailyRoutineResponse)
async def update_routine(
    routine_id: UUID,
    data: DailyRoutineUpdate,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Update a planner event."""
    service = DailyRoutineService(session)
    try:
        updated = await service.update_routine(routine_id, current_user.id, data)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    if not updated:
        raise HTTPException(status_code=404, detail="Routine not found")
    await session.commit()
    return updated


@router.patch("/{routine_id}/status", response_model=DailyRoutineResponse)
async def update_routine_status(
    routine_id: UUID,
    data: DailyRoutineStatusUpdate,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Mark a planner event planned, completed, or skipped."""
    service = DailyRoutineService(session)
    updated = await service.update_status(routine_id, current_user.id, data.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Routine not found")
    await session.commit()
    return updated


@router.delete("/{routine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_routine(
    routine_id: UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Delete a planner event."""
    service = DailyRoutineService(session)
    deleted = await service.delete_routine(routine_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Routine not found")
    await session.commit()

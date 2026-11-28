"""Impact tracker API module (Phase 7)."""
from datetime import date
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_async_session
from app.modules.emission_factors.schema import EmissionFactorListResponse
from app.modules.emission_factors.service import EmissionFactorService
from app.modules.impact_records.schema import (
    ImpactCalculationPreview,
    ImpactRecordListResponse,
    ImpactRecordResponse,
    ImpactSummaryResponse,
    TransportImpactRequest,
)
from app.modules.impact_records.service import ImpactService
from app.modules.users.models import UserModel
from app.modules.users.routes import get_current_active_user

router = APIRouter(tags=["impact"])


@router.get("/factors", response_model=EmissionFactorListResponse)
async def get_impact_factors(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Return emission factor references used by the calculator."""
    res = await EmissionFactorService(session).list_factors()
    await session.commit()
    return res


@router.post("/calculate", response_model=ImpactCalculationPreview)
async def preview_impact_calculation(
    payload: TransportImpactRequest,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Dry-run reproducible CO2e calculation without persisting."""
    service = ImpactService(session)
    try:
        res = await service.preview_calculation(payload)
        await session.commit()
        return res
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/activities", response_model=ImpactRecordResponse, status_code=status.HTTP_201_CREATED)
async def log_impact_activity(
    payload: TransportImpactRequest,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Log an eco activity and persist an impact record with factor snapshot."""
    service = ImpactService(session)
    try:
        record = await service.log_activity(current_user.id, payload)
        await session.commit()
        return record
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/summary", response_model=ImpactSummaryResponse)
async def get_impact_summary(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    date_from: Optional[date] = Query(None, alias="from"),
    date_to: Optional[date] = Query(None, alias="to"),
    period: Optional[str] = Query("30d", description="today, week, 30d"),
):
    """Get estimated CO2e savings summary, daily trend, and mode breakdown."""
    service = ImpactService(session)
    return await service.get_summary(
        user_id=current_user.id,
        date_from=date_from,
        date_to=date_to,
        period=None if (date_from or date_to) else period,
    )


@router.get("/records", response_model=ImpactRecordListResponse)
async def list_impact_records(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    date_from: Optional[date] = Query(None, alias="from"),
    date_to: Optional[date] = Query(None, alias="to"),
    period: Optional[str] = Query(None),
):
    """List logged impact records for the user."""
    service = ImpactService(session)
    return await service.list_records(
        user_id=current_user.id,
        date_from=date_from,
        date_to=date_to,
        period=period,
    )


@router.get("/records/{record_id}", response_model=ImpactRecordResponse)
async def get_impact_record_detail(
    record_id: UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Get calculation provenance and factor snapshot for one record."""
    service = ImpactService(session)
    rec = await service.get_record(record_id, current_user.id)
    if not rec:
        raise HTTPException(status_code=404, detail="Impact record not found")
    return rec


@router.delete("/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_impact_record(
    record_id: UUID,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Delete an impact record owned by the current user."""
    service = ImpactService(session)
    deleted = await service.delete_record(record_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Impact record not found")
    await session.commit()

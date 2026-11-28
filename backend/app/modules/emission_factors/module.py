"""Emission factors API module (Phase 7)."""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_async_session
from app.modules.emission_factors.schema import EmissionFactorListResponse
from app.modules.emission_factors.service import EmissionFactorService
from app.modules.users.models import UserModel
from app.modules.users.routes import get_current_active_user

router = APIRouter(tags=["emission-factors"])


@router.get("", response_model=EmissionFactorListResponse)
async def list_emission_factors(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Return curated emission factor references with sources and units."""
    service = EmissionFactorService(session)
    res = await service.list_factors()
    await session.commit()
    return res

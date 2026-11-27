"""User profile routes (Phase 2)."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_async_session
from app.modules.user_profiles.models import UserProfileModel
from app.modules.user_profiles.schema import (
    UserProfileCreate,
    UserProfileResponse,
    UserProfileUpdate,
)
from app.modules.user_profiles.service import UserProfileService
from app.modules.users.routes import get_current_active_user
from app.modules.users.models import UserModel

router = APIRouter(tags=["profile"])


@router.get("", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Get current user's profile."""
    service = UserProfileService(session)
    profile = await service.get_by_user_id(current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Please complete onboarding.")
    return profile


@router.post("", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_user_profile(
    profile_data: UserProfileCreate,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Create current user's profile."""
    service = UserProfileService(session)

    # Check if profile already exists
    existing = await service.get_by_user_id(current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists. Use PATCH to update."
        )

    profile = await service.create(current_user.id, profile_data)
    await session.commit()
    return profile


@router.patch("", response_model=UserProfileResponse)
async def update_current_user_profile(
    profile_data: UserProfileUpdate,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Update current user's profile."""
    service = UserProfileService(session)
    profile = await service.get_by_user_id(current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Please complete onboarding.")

    updated_profile = await service.update(profile.id, profile_data)
    await session.commit()
    return updated_profile


@router.post("/upsert", response_model=UserProfileResponse)
async def upsert_user_profile(
    profile_data: UserProfileCreate,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Create or update current user's profile (upsert)."""
    service = UserProfileService(session)
    profile = await service.upsert(current_user.id, profile_data)
    await session.commit()
    return profile
"""User profile service layer with business logic."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.user_profiles.models import UserProfileModel
from app.modules.user_profiles.schema import UserProfileCreate, UserProfileUpdate, UserProfileResponse


class UserProfileService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: UUID) -> Optional[UserProfileModel]:
        """Get user profile by user ID."""
        result = await self.session.execute(
            select(UserProfileModel).where(UserProfileModel.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, profile_id: UUID) -> Optional[UserProfileModel]:
        """Get user profile by profile ID."""
        result = await self.session.execute(
            select(UserProfileModel).where(UserProfileModel.id == profile_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: UUID, profile_data: UserProfileCreate) -> UserProfileModel:
        """Create a new user profile."""
        profile = UserProfileModel(
            user_id=user_id,
            **profile_data.model_dump()
        )
        self.session.add(profile)
        await self.session.flush()
        return profile

    async def update(self, profile_id: UUID, profile_data: UserProfileUpdate) -> Optional[UserProfileModel]:
        """Update user profile fields."""
        profile = await self.get_by_id(profile_id)
        if not profile:
            return None

        update_data = profile_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)

        profile.updated_at = datetime.utcnow()
        await self.session.flush()
        return profile

    async def upsert(self, user_id: UUID, profile_data: UserProfileCreate) -> UserProfileModel:
        """Create or update user profile (upsert)."""
        existing = await self.get_by_user_id(user_id)
        if existing:
            update_data = profile_data.model_dump()
            for field, value in update_data.items():
                setattr(existing, field, value)
            existing.updated_at = datetime.utcnow()
            await self.session.flush()
            return existing
        else:
            return await self.create(user_id, profile_data)
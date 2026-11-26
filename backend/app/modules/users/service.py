"""User service layer with password hashing and business logic."""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.repository import UserModel
from app.modules.users.schema import UserCreate, UserUpdate, UserResponse, Token, TokenPayload
from app.core.config import get_settings

settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    async def get_by_email(self, email: str) -> Optional[UserModel]:
        """Get user by email address."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: UUID) -> Optional[UserModel]:
        """Get user by ID."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_data: UserCreate) -> UserModel:
        """Create a new user with hashed password."""
        hashed_password = self.hash_password(user_data.password)
        user = UserModel(
            email=user_data.email,
            hashed_password=hashed_password,
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def update(self, user_id: UUID, user_data: UserUpdate) -> Optional[UserModel]:
        """Update user fields."""
        user = await self.get_by_id(user_id)
        if not user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.utcnow()
        await self.session.flush()
        return user

    async def authenticate(self, email: str, password: str) -> Optional[UserModel]:
        """Authenticate user with email and password."""
        user = await self.get_by_email(email)
        if not user or not user.is_active:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
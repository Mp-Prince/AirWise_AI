"""SQLAlchemy engine + session factory.

The engine is created lazily so the app can boot (Phase 0 smoke test)
without a running PostgreSQL server; it is only connected when a
session is first requested.
"""
from collections.abc import Generator
from contextlib import asynccontextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

_engine = None
_SessionFactory: sessionmaker[Session] | None = None

_async_engine = None
_AsyncSessionFactory: async_sessionmaker[AsyncSession] | None = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(
            get_settings().DATABASE_URL,
            pool_pre_ping=True,
            future=True,
        )
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = sessionmaker(bind=get_engine(), future=True)
    return _SessionFactory


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields one session per request."""
    with get_session_factory()() as session:
        try:
            yield session
        finally:
            session.close()


def get_async_engine():
    """Get async engine for async operations."""
    global _async_engine
    if _async_engine is None:
        # Convert sync URL to async URL (postgresql+psycopg -> postgresql+asyncpg)
        db_url = get_settings().DATABASE_URL
        if db_url.startswith("postgresql+psycopg://"):
            db_url = db_url.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)
        _async_engine = create_async_engine(
            db_url,
            pool_pre_ping=True,
            future=True,
        )
    return _async_engine


def get_async_session_factory() -> async_sessionmaker[AsyncSession]:
    global _AsyncSessionFactory
    if _AsyncSessionFactory is None:
        _AsyncSessionFactory = async_sessionmaker(
            bind=get_async_engine(),
            expire_on_commit=False,
        )
    return _AsyncSessionFactory


async def get_async_session() -> Generator[AsyncSession, None, None]:
    """FastAPI dependency that yields one async session per request."""
    async with get_async_session_factory()() as session:
        try:
            yield session
        finally:
            await session.close()

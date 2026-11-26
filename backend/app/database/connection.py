"""SQLAlchemy engine + session factory.

The engine is created lazily so the app can boot (Phase 0 smoke test)
without a running PostgreSQL server; it is only connected when a
session is first requested.
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

_engine = None
_SessionFactory: sessionmaker[Session] | None = None


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

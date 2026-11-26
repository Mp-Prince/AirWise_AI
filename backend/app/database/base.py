"""Declarative base shared by all entity models (Phase 1 onwards)."""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

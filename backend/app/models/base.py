"""Общий DeclarativeBase канонической схемы."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Метаданные ORM; типы PG объявляет миграция Alembic."""

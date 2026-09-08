"""Базовый класс для всех SQLAlchemy-моделей."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Корневой класс, от которого наследуются все модели."""

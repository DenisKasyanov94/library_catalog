"""Pydantic-схемы книги."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BookCreate(BaseModel):
    """Схема создания книги (POST)."""

    title: str = Field(..., min_length=1, max_length=500)
    author: str = Field(..., min_length=1, max_length=300)
    year: int = Field(..., ge=0, le=2100)
    genre: str = Field(..., min_length=1, max_length=100)
    pages: int = Field(..., gt=0)
    available: bool = True
    isbn: str | None = Field(None, max_length=20)
    description: str | None = None
    extra: dict | None = None


class BookUpdate(BaseModel):
    """Схема обновления книги (PUT/PATCH)."""

    title: str | None = None
    author: str | None = None
    year: int | None = None
    genre: str | None = None
    pages: int | None = None
    available: bool | None = None
    isbn: str | None = None
    description: str | None = None
    extra: dict | None = None


class BookRead(BaseModel):
    """Схема ответа (GET)."""

    model_config = ConfigDict(from_attributes=True)

    book_id: UUID
    title: str
    author: str
    year: int
    genre: str
    pages: int
    available: bool
    isbn: str | None
    description: str | None
    extra: dict | None
    created_at: datetime
    updated_at: datetime

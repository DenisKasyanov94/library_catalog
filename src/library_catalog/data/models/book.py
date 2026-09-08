"""Модель книги."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from library_catalog.data.models.base import Base


class Book(Base):
    __tablename__ = "books"

    book_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    title: Mapped[str] = mapped_column(String(500), index=True)
    author: Mapped[str] = mapped_column(String(300), index=True)
    year: Mapped[int] = mapped_column(index=True)
    genre: Mapped[str] = mapped_column(String(100), index=True)
    pages: Mapped[int]
    available: Mapped[bool] = mapped_column(default=True, index=True)
    isbn: Mapped[str | None] = mapped_column(String(20), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    extra: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )

"""Мапперы: преобразование Book (ORM) ↔ Pydantic-схемы."""

from library_catalog.api.v1.schemas.book import BookCreate, BookRead
from library_catalog.data.models.book import Book


def to_book_read(book: Book) -> BookRead:
    """Превращает ORM-модель Book в схему ответа BookRead."""
    return BookRead.model_validate(book)


def to_book(data: BookCreate) -> Book:
    """Создаёт ORM-модель Book из схемы BookCreate (без сохранения в БД)."""
    return Book(**data.model_dump())

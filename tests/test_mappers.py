"""Тесты мапперов модель ↔ схема."""

from datetime import datetime
from uuid import uuid4

from library_catalog.api.v1.schemas.book import BookCreate
from library_catalog.data.models.book import Book
from library_catalog.domain.mappers.book import to_book, to_book_read


def test_to_book_builds_model() -> None:
    data = BookCreate(title="A", author="B", year=2000, genre="G", pages=10)
    book = to_book(data)
    assert isinstance(book, Book)
    assert book.title == "A"
    assert book.author == "B"


def test_to_book_read_maps_fields() -> None:
    book = Book(
        book_id=uuid4(),
        title="A",
        author="B",
        year=2000,
        genre="G",
        pages=10,
        available=True,
        isbn=None,
        description=None,
        extra=None,
        created_at=datetime(2020, 1, 1),
        updated_at=datetime(2020, 1, 1),
    )
    result = to_book_read(book)
    assert result.title == "A"
    assert result.book_id == book.book_id
    assert result.available is True

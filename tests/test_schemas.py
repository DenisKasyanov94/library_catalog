"""Тесты Pydantic-схем книги."""

import pytest
from pydantic import ValidationError

from library_catalog.api.v1.schemas.book import BookCreate, BookRead, BookUpdate


def test_book_create_defaults() -> None:
    book = BookCreate(
        title="Гарри Поттер",
        author="Дж. Роулинг",
        year=1997,
        genre="Фэнтези",
        pages=223,
    )
    assert book.available is True
    assert book.isbn is None
    assert book.description is None
    assert book.extra is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title", ""),
        ("pages", 0),
        ("year", -1),
    ],
)
def test_book_create_validation_errors(field: str, value: object) -> None:
    payload: dict[str, object] = {
        "title": "A", "author": "B", "year": 2000, "genre": "G", "pages": 10,
    }
    payload[field] = value
    with pytest.raises(ValidationError):
        BookCreate(**payload)


def test_book_update_all_optional() -> None:
    book = BookUpdate()
    assert book.title is None
    assert book.year is None


def test_book_read_requires_id() -> None:
    with pytest.raises(ValidationError):
        BookRead(title="A", author="B", year=2000, genre="G", pages=10, available=True)

"""Сервисный слой для работы с книгами."""

from uuid import UUID

from library_catalog.api.v1.schemas.book import BookCreate, BookRead, BookUpdate
from library_catalog.data.repositories.book_repository import BookRepository
from library_catalog.domain.mappers.book import to_book_read


class BookService:
    """Бизнес-логика работы с книгами поверх BookRepository."""

    def __init__(self, repository: BookRepository) -> None:
        self.repository = repository

    async def create_book(self, data: BookCreate) -> BookRead:
        """Создаёт книгу из схемы BookCreate и возвращает BookRead."""
        book = await self.repository.create(**data.model_dump())
        return to_book_read(book)

    async def get_book(self, book_id: UUID) -> BookRead | None:
        """Возвращает книгу по id или None, если её нет."""
        book = await self.repository.get_by_id(book_id)
        return to_book_read(book) if book else None

    async def list_books(self, limit: int = 20, offset: int = 0) -> list[BookRead]:
        """Возвращает список книг с пагинацией."""
        books = await self.repository.get_all(limit=limit, offset=offset)
        return [to_book_read(book) for book in books]

    async def search_books(
        self,
        title: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        year: int | None = None,
        available: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[BookRead]:
        """Ищет книги по фильтрам (непустые параметры добавляют условие)."""
        books = await self.repository.find_by_filters(
            title=title,
            author=author,
            genre=genre,
            year=year,
            available=available,
            limit=limit,
            offset=offset,
        )
        return [to_book_read(book) for book in books]

    async def update_book(self, book_id: UUID, data: BookUpdate) -> BookRead | None:
        """Обновляет только переданные поля книги."""
        book = await self.repository.update(
            book_id,
            **data.model_dump(exclude_unset=True),
        )
        return to_book_read(book) if book else None

    async def delete_book(self, book_id: UUID) -> bool:
        """Удаляет книгу; возвращает True, если она была."""
        return await self.repository.delete(book_id)

"""Роутер CRUD для книг."""

from collections.abc import AsyncIterator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from library_catalog.api.v1.schemas.book import BookCreate, BookRead, BookUpdate
from library_catalog.core.database import async_session_factory
from library_catalog.data.repositories.book_repository import BookRepository
from library_catalog.domain.services.book_service import BookService

router = APIRouter(prefix="/books", tags=["books"])


async def get_session() -> AsyncIterator[AsyncSession]:
    """Отдаёт сессию БД на время обработки запроса."""
    async with async_session_factory() as session:
        yield session


async def get_book_service(session: AsyncSession = Depends(get_session)) -> BookService:
    """Собирает BookService с репозиторием, привязанным к сессии."""
    return BookService(BookRepository(session))


@router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED)
async def create_book(
    data: BookCreate,
    service: BookService = Depends(get_book_service),
) -> BookRead:
    """Создаёт книгу."""
    return await service.create_book(data)


@router.get("", response_model=list[BookRead])
async def list_books(
    title: str | None = None,
    author: str | None = None,
    genre: str | None = None,
    year: int | None = None,
    available: bool | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: BookService = Depends(get_book_service),
) -> list[BookRead]:
    """Возвращает список книг с фильтрами и пагинацией."""
    return await service.search_books(
        title=title,
        author=author,
        genre=genre,
        year=year,
        available=available,
        limit=limit,
        offset=offset,
    )


@router.get("/{book_id}", response_model=BookRead)
async def get_book(
    book_id: UUID,
    service: BookService = Depends(get_book_service),
) -> BookRead:
    """Возвращает книгу по id или 404."""
    book = await service.get_book(book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена")
    return book


@router.put("/{book_id}", response_model=BookRead)
async def update_book(
    book_id: UUID,
    data: BookUpdate,
    service: BookService = Depends(get_book_service),
) -> BookRead:
    """Обновляет книгу или 404."""
    book = await service.update_book(book_id, data)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена")
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: UUID,
    service: BookService = Depends(get_book_service),
) -> None:
    """Удаляет книгу или 404."""
    deleted = await service.delete_book(book_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена")

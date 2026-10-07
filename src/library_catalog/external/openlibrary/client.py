"""Клиент Open Library API для поиска книг."""

from typing import Any

import httpx

from library_catalog.external.base.http_client import BaseHTTPClient


class OpenLibraryClient:
    """Поиск книг в открытом каталоге Open Library."""

    BASE_URL = "https://openlibrary.org"

    def __init__(self, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._http = BaseHTTPClient(self.BASE_URL, transport=transport)

    async def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Ищет книги по запросу и возвращает список словарей."""
        data = await self._http.get_json(
            "/search.json",
            params={"q": query, "limit": limit},
        )
        docs: list[dict[str, Any]] = data.get("docs", [])
        return [
            {
                "title": doc.get("title"),
                "author": (doc.get("author_name") or [None])[0],
                "year": doc.get("first_publish_year"),
                "isbn": (doc.get("isbn") or [None])[0],
            }
            for doc in docs
        ]

    async def close(self) -> None:
        """Закрывает HTTP-клиент."""
        await self._http.close()

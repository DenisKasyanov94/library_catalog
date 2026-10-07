"""Тесты клиента Open Library с моком httpx."""

import httpx
import pytest

from library_catalog.external.openlibrary.client import OpenLibraryClient


def _handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "docs": [
                {
                    "title": "Гарри Поттер",
                    "author_name": ["Дж. Роулинг"],
                    "first_publish_year": 1997,
                    "isbn": ["978-5-389-07435-4"],
                }
            ]
        },
    )


@pytest.mark.asyncio
async def test_search_returns_parsed_books() -> None:
    client = OpenLibraryClient(transport=httpx.MockTransport(_handler))
    try:
        results = await client.search("гарри")
    finally:
        await client.close()

    assert len(results) == 1
    assert results[0]["title"] == "Гарри Поттер"
    assert results[0]["author"] == "Дж. Роулинг"
    assert results[0]["year"] == 1997
    assert results[0]["isbn"] == "978-5-389-07435-4"

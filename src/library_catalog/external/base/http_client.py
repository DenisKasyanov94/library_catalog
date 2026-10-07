"""Базовый асинхронный HTTP-клиент для внешних API."""

from typing import Any

import httpx


class BaseHTTPClient:
    """Обёртка над httpx.AsyncClient."""

    def __init__(
        self,
        base_url: str,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url,
            transport=transport,
            timeout=10.0,
        )

    async def get_json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Выполняет GET и возвращает распарсенный JSON."""
        response = await self._client.get(path, params=params)
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        """Закрывает HTTP-клиент."""
        await self._client.aclose()

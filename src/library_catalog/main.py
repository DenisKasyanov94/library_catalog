"""Точка входа FastAPI приложения Library Catalog."""

from fastapi import FastAPI

from library_catalog.api.v1.routers.books import router as books_router
from library_catalog.core.config import settings

app = FastAPI(
    title="Library Catalog API",
    description="REST API для управления библиотечным каталогом",
    version="1.0.0",
)

app.include_router(books_router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return {"message": "Welcome to Library Catalog API"}


@app.get("/health")
async def health_check():
    """Health check эндпоинт."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

# Library Catalog API

REST API для управления библиотечным каталогом.
Учебный проект: FastAPI + PostgreSQL + SQLAlchemy 2.0 (async) + Alembic.

## Стек
- FastAPI, Uvicorn
- PostgreSQL 16, async SQLAlchemy 2.0, asyncpg
- Alembic (миграции), Pydantic (валидация)
- httpx (внешний API Open Library)
- Poetry (зависимости)

## Запуск
```bash
# 1. Поднять БД
docker compose up -d postgres

# 2. Установить зависимости
poetry install

# 3. Запустить сервер
poetry run uvicorn library_catalog.main:app --reload
```

Swagger: http://127.0.0.1:8000/docs

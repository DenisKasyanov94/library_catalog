# Заметки о реализации

## T-04: Сервисный слой BookService
- Дата: 2026-10-07
- Изменённые файлы:
  - `src/library_catalog/domain/services/book_service.py` (новый)
  - `src/library_catalog/domain/services/__init__.py` (ре-экспорт)
- Ключевые решения:
  - `BookService` — тонкий слой бизнес-логики поверх `BookRepository`, без прямой работы с БД.
  - `create_book` передаёт в репозиторий `**data.model_dump()` из `BookCreate`.
  - `update_book` использует `data.model_dump(exclude_unset=True)` — обновляются только переданные поля.
  - Методы-читалки (`get_book`, `list_books`, `search_books`, `update_book`) возвращают `BookRead | None` / `list[BookRead]` через маппер `to_book_read`.
- Известные ограничения: не выявлено.

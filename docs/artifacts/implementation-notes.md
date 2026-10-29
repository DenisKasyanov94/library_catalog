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
## T-05: CRUD-роутеры
- Дата: 2026-10-07
- Файлы: `src/library_catalog/api/v1/routers/books.py` (новый), `src/library_catalog/main.py`.
- Решения:
  - `get_session` (сессия на запрос) и `get_book_service` (сборка репозитория + сервиса) через `Depends`.
  - Эндпоинты: POST / GET-list / GET-id / PUT / DELETE + `/external-search`.
  - `/external-search` объявлен ДО `/{book_id}` (иначе слово распознаётся как UUID и даёт 422).

## T-06: Open Library + тесты
- Дата: 2026-10-07
- Файлы: `external/base/http_client.py`, `external/openlibrary/client.py`,
  `tests/test_schemas.py`, `tests/test_mappers.py`, `tests/test_openlibrary.py`.
- Решения:
  - `BaseHTTPClient` принимает `transport` → тесты через `httpx.MockTransport` без сети.
  - `OpenLibraryClient.search` → `https://openlibrary.org/search.json`.
  - 9 тестов зелёные.

## Code review (2026-10-26): changes requested
- Источник: `D:\projects\ForLook\code_review_feature_books_api.md`.
- Найдено 12 дефектов: 500 вместо 409/422/502/504, слабая валидация `BookUpdate`, wildcard в поиске и др.
- План фиксов: `docs/artifacts/07-fix-sprint-plan.md` (F-01…F-09; батч 1 = критичные).
- Известные ограничения: см. ревью (обработка ошибок, валидация, поиск, тесты API).

## Фикс-раунд QA батча 2 — `agent-system` (2026-10-29)
- Объект: `d:\vscode-data\User\prompts` (HEAD `7581fa6`); источник замечаний — `docs/artifacts/qa-report-batch2.md` (вердикт FAIL).
- Закрыто:
  - **B-1** — единственный дом «порога церемонии» остаётся `agent-system/quality-gates.spec.md` §1; четыре копии критерия в `qa-engineer.agent.md`, `code-reviewer.agent.md`, `agent-system/remember-closeout.instructions.md`, `agent-capabilities.md` заменены ссылкой на §1 (+ §2 для артефактов).
  - **M-1/M-2** — живые указатели на несуществующий `AGENTS.md` (решение D-08) перенаправлены: `qa-engineer.agent.md` §«Выходной артефакт» → §1; протокол «вспомни!» — обязательный файл №1 теперь `agent-capabilities.md` (матрица делегирования + §«Правила для Team Lead (напоминание)»).
  - **m-1** — `mock_justification` в шаблоне `tl2dev` помечен: пустой список невалиден для `feature` (`--validate-contract` → exit 1), заполняется обоснованием мока или `n/a: моков нет`; `already_in_context: []` явно помечен как допустимый.
  - **m-2** — номера строк убраны из §6 `quality-gates.spec.md` (дрейфуют), ориентир — §-заголовки; очередь D3 помечена закрытой, строка D3 в `upgrade-plan-2026-10-28.md` переведена в Done.
- Строки (до → после): `qa-engineer.agent.md` 197 → 197, `code-reviewer.agent.md` 241 → 241, `agent-capabilities.md` 126 → 126, `remember-closeout.instructions.md` 57 → 57, `team-lead.agent.md` 444 → 444, `handoff-contracts.spec.md` 149 → 149, `quality-gates.spec.md` 146 → 146 — правки внутристрочные, роста `.agent.md` нет (0%).
- Не сделано (зона `developer`): коммит в `d:\vscode-data\User\prompts` и строка `journal.py append-result` — терминала у `tech-writer` нет (шов `proxy_writer`).


## T-08 — фикс-раунд QA (BL-1: смешанные naive/aware `ts`)
- Дата: 2026-10-29 | Коммит: `8cc10d1` (`d:\vscode-data\User\prompts`, remote нет)
- Изменённые файлы: `agent-system/tools/journal.py`
- Ключевые решения:
  - одна точка нормализации `as_utc_naive()` (aware → UTC без `tzinfo`, naive = UTC), применена в `parse_since()` и `_record_ts()`; формат хранения и `now_iso()` не менялись;
  - регресс в `--self-test`: `_selftest_time_window()` — 5 проверок (naive vs aware `--since`, aware `ts` vs naive `--since`, naive=UTC, `audit` на смешанном журнале, `done` в смешанный журнал); итого 231 checks (было 226).
- Известные ограничения: замечания QA П-2 (цифра 117 vs 115) и П-3 (трейсбек не-`ContractError` в `main()`) не закрывались — вне BL-1.

## T-08 — фикс-раунд CR-3 (`ui` отсутствовал в профилях задачи)
- Дата: 2026-10-29 | Коммит: `c9f14cb` (`d:\vscode-data\User\prompts`, remote нет)
- Изменённые файлы: `agent-system/tools/journal.py`, `agent-system/handoff-contracts.spec.md`, `agent-system/session-journal.spec.md`, `team-lead.agent.md` (+158 / −35).
- Ключевые решения:
  - `ui` добавлен в `TL2DEV_PROFILES` — один набор на словарь события, матрицу контракта и гейт `done`; `DONE_GATE_REQUIREMENTS["ui"] = ("qa","cr")`, `DONE_GATE_MIN_LEVEL["ui"] = "light"` по `quality-gates.spec.md` §2;
  - единый источник имён — `team-profiles.yaml`: `TEAM_PROFILES_FILE`, явные alias `new_feature→feature` / `deploy→infra`, `routing` как непрофильная запись; `team_profiles_from_yaml()` парсит fenced-yaml без PyYAML;
  - регресс в `--self-test`: `_selftest_profile_source()` + `_tl2dev_ui_contract()` — 6 проверок, итого 249 checks (было 243).
- Известные ограничения: UI-матрица контракта зеркалит `feature` (в спеках отдельного набора для UI нет) — при ином решении правится одна колонка `TL2DEV_MATRIX`.

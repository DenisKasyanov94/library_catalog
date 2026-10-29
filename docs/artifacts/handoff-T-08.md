# Handoff T-08 — отчёт разработчика

- **Задача:** T-08 (② C1-lite, профиль `infra`, `normal`)
- **Статус:** done
- **Коммит:** `4f4cfc4` (репозиторий `d:\vscode-data\User\prompts`, remote отсутствует — пуш не требуется)
- **Дата:** 2026-10-29
- **Изменённые файлы:** `agent-system/tools/journal.py`, `agent-system/upgrade-plan-2026-10-28.md` (незакоммиченные правки T-08 сохранены, не откатывались)

## Что чинилось (4 FAIL из `--self-test`)

### 1. «гейт done: без --since те же исторические done считаются → block»

**Причина:** не в гейте, а в самой проверке. Утверждение требовало `"done" not in _journal_events(legacy)`,
но в журнале-фикстуре уже лежат 4 исторических `done` (3 старых + T-10, принятый в предыдущей
проверке), поэтому условие не могло стать истинным ни при каком поведении кода.

**Факт поведения (проверено отдельным прогоном):** без `--since` `since=None` → режим `auto`,
в окне считаются все 4 `done` → бюджет warn-режима (3) исчерпан → `block`, exit 1, запись не выполнена.

**Правка:** снимок состава журнала до вызова + сравнение после (`_journal_events(legacy) == events_before`) —
проверка теперь выражает «записи нет», а не «в журнале нет ни одного `done`». Семантика гейта
не менялась (grandfathering работает только при явном `--since`, как в validation_rules).

### 2–3. «стражник (а): распознано 0 / не распознано 0» и «испорченная ссылка на копии»

**Причина 1 (главная):** `PROMPTS_ROOT = dirname(dirname(__file__))` давал `…\prompts\agent-system`,
а не корень системы агентов → `_scan_targets` искал `agent-system/agent-system/*.md` и
`*.agent.md` внутри `agent-system` — целей ноль, стражник проходил «вхолостую» (0 ссылок = 0 проблем).
Исправлено на три уровня (`…\prompts`); `read_text` к тому же молча отдавал `""` для
несуществующего `team-lead.agent.md`, из-за чего падал и стражник (б).

**Причина 2:** одна ссылка может нести несколько якорей (`файл.md §«A» и §5`, `файл.md §1, §2`),
а сканер считал только первый якорь → `got == 1` вместо 2 на копии. Добавлен `_ref_anchors()`:
первый `§…` + продолжения по связке `,`/`;`/`.`/`и`/`&`, если за связкой стоит `§`.

**Итог на живом дереве:** распознано **109** ссылок, неразрешённых **0**, нераспознанных форм **0**.

### 4. «стражник (б): ключи шаблона handoff == TL2DEV_MATRIX (17 полей)»

**Причина:** тот же `PROMPTS_ROOT` — `team-lead.agent.md` читался по несуществующему пути,
`handoff_template_keys("")` возвращал пустое множество. После правки: **17 ключей шаблона ==
17 ключей `TL2DEV_MATRIX`**, `team-lead.agent.md` править не потребовалось (расхождения не было).

## Проверки (реальный вывод)

| Проверка | Результат |
|---|---|
| `python agent-system\tools\journal.py --self-test` | **exit 0**, `SELF-TEST OK (226 checks)` — 226 > 198 |
| `python -m py_compile agent-system\tools\journal.py` | exit 0 |
| `reference_guard()` | recognized=109, unresolved=0, bad_form=0 |
| `template_guard()` | keys == matrix_keys (17 == 17) |
| `git status --short` | пусто |

Note: `py -3` в этой оболочке падает на пути с не-ASCII (`Unable to create process`, Python 3.14),
поэтому проверки гонялись через `python` (3.12.6). Это окружение, не код.

## Известные ограничения / аномалии

1. **Стражник (а) впервые реально смотрит на дерево** (до правки он был декоративным). Сейчас
   он покрывает 12 `*.agent.md` + 21 `agent-system/*.md`; ссылки на артефакты проекта
   (`docs/artifacts/*`) намеренно не резолвятся и пропускаются по списку `REF_EXTERNAL_RE` —
   новый тип имени файла в проекте потребует расширения списка.
2. **`--gate-mode` warn→block без `--since`**: на боевом журнале по-прежнему обязателен `--since`
   (`invalid_since`), grandfathering иначе стал бы декоративным.
3. **Формулировка «без `--since` исторические done не блокируют»** несовместима с проверкой
   «без `--since` те же done считаются → block» и с `validation_rules` (`--since` пустой =
   гейт по всему журналу). Оставлено поведение по спеке; поправлено только утверждение теста.
4. **Не тронуто:** сам код гейтов (`done_gate_check`, `resolve_done_gate_mode`, `open_incidents`,
   `audit`) в этой сессии не менялся — их проверки проходили и до правок.

## Фикс-раунд QA (BL-1)

- **Дата:** 2026-10-29 | **Коммит:** `8cc10d1` (репозиторий `d:\vscode-data\User\prompts`, remote нет — пуш невозможен)
- **Изменённые файлы:** `agent-system/tools/journal.py` (+67 / −6)
- **Блокер BL-1:** `--since` падал `TypeError: can't compare offset-naive and offset-aware datetimes`
  в `in_gate_window` — в боевом журнале `ts` смешаны (naive 83 / aware 34 у `done`), поэтому
  `done` нельзя было записать ни в одном `--gate-mode`, а `audit --since` не печатал ничего.

**Правка (одна точка нормализации):** добавлена `as_utc_naive(moment)` — aware приводится к UTC и
снимается `tzinfo`, naive трактуется как UTC. Через неё проходят ОБЕ стороны сравнения:
`parse_since()` (`--since`) и `_record_ts()` (метка записи). Формат хранения событий не менялся,
`now_iso()` не тронут, журнал append-only.

**Регресс в `--self-test`** (`_selftest_time_window`, 5 проверок): `--since` naive == `--since` aware
(`2026-10-29` vs `2026-10-29T03:00:00+03:00`); aware `ts` vs naive `--since` без `TypeError`;
naive трактуется как UTC; `audit` на журнале naive+aware → exit 0 / нарушений 0; `done`
принимается в журнал со смешанными метками. **Негатив проверен:** тот же журнал на коде `HEAD~1`
(`4f4cfc4`) → трейсбек `TypeError`, exit 1, stdout пуст.

| Проверка | Результат |
|---|---|
| `python agent-system\tools\journal.py --self-test` | **exit 0**, `SELF-TEST OK (231 checks)` (было 226) |
| `python -m py_compile agent-system\tools\journal.py` | exit 0 |
| копия боевого журнала (601 строка, 1 битая): `audit --since 2026-10-28` | exit 1 (**отказ, не падение**): grandfathering 106, в окне 11 `done`, 11 нарушений |
| копия боевого журнала: `audit --since 2026-10-29` | exit 1: grandfathering **115**, в окне 2 (`A4`, `A5`), 2 нарушения |
| копия боевого журнала: `verdict(pass)+review(approved)` с `ts=+03:00`, затем `done` с naive `ts` | оба `exit 0`, `tail_events=['verdict','review','done']` |
| боевой журнал | `sha256=96a24400…` до и после — не изменён, append-only соблюдён |
| `git status --short` | пусто |

**Аномалии фикс-раунда:**
1. `git remote` в `d:\vscode-data\User\prompts` отсутствует → `git push` физически невозможен,
   коммит `8cc10d1` только локальный (как и предыдущий `4f4cfc4`).
2. Остаются замечания QA, НЕ входившие в BL-1 и не исправленные: П-2 (доки говорят «117
   исторических `done`», фактически 115 до `2026-10-29` + 2 в окне — A4/A5), П-3 (не-`ContractError`
   исключения в `main()` по-прежнему выходят трейсбеком с exit 1, неотличимо от `block`).
3. `audit --since 2026-10-28` / `2026-10-29` на боевом журнале даёт exit 1 с нарушениями по
   историческим задачам (A1–A5, T-01..T-06 и др.) — это ожидаемый grandfathering-разрыв
   (задачи закрывались до введения гейта), не регресс; выбор `--since` за team-lead.

## Фикс-раунд CR

- **Дата:** 2026-10-29 | **Коммит:** `56ea9a0` (репозиторий `d:\vscode-data\User\prompts`, remote нет — пуш невозможен)
- **Изменённые файлы (4):** `agent-system/tools/journal.py`, `agent-system/quality-gates.spec.md`,
  `agent-system/session-journal.spec.md`, `agent-system/remember-closeout.instructions.md`
  (+221 / −44). Коммит один: `fix(agent-system): T-08 CR-fix - profile from task_assigned, audit waiver, --since documented`.
- **Замечания CR (`docs/artifacts/code-review-T-08.md`):** Major 1 — профиль задачи занижался
  самозаявленным `payload.profile` внутри `done`, feature-задача закрывалась под `docs` и гейт
  обходился; Major 2 — легальный waiver (`--allow-missing-gates`) не учитывался в `audit`,
  поэтому аудит после легального пропуска оставался красным навсегда; Minor — `--since` и состав
  гейтов не были описаны в спеках, которыми пользуются агенты.

**Правки:**

1. **Major 1 — профиль ТОЛЬКО из `task_assigned`.** `task_profile(records, task, hint)` →
   `journal_profile(records, task)`: читается исключительно событие `task_assigned`
   (`DONE_GATE_PROVENANCE_EVENT`), самозаявленный `profile` записи `done` на состав гейтов больше
   не влияет — печатается предупреждение (`declared_profile()` оставлен только для диагностики).
   `done_gate_check()` теперь возвращает 5-й элемент `confirmed` (был ли `task_assigned`); при его
   отсутствии профиль не подтверждён и запись разрешают только `--gate-mode` (warn/block) или
   waiver; текст отказа формирует `gate_gap_text(missing, confirmed)`.
2. **Major 2 — waiver виден аудиту.** Добавлена `task_waivers(records, task, since)`: `audit`
   собирает `decision{about: "done-gate", choice: "waiver"}` в окне и исключает задачу из
   `violations` — печатает строку `WAIVER: <ts> <task> (профиль …) — пропуск по decision team-lead: <reason>`,
   итог `done в окне: N, нарушений: K, waiver: M`; при `K=0` — exit 0. Waiver другой задачи
   нарушение не закрывает (проверено тестом).
3. **Minor — документация.** `session-journal.spec.md`: новый §«Гейт `done` — состав по профилю»
   (таблица «состав гейтов / окно / нет `task_assigned` / `--gate-mode` / warn / block / waiver /
   сверка» + канонический вызов для PowerShell 5.1 с `--%`). `quality-gates.spec.md` §2: формулировка
   «связка `verdict.gates` ↔ `done` не валидируется — цель на C1» заменена на «Правило закрытия —
   валидируется инструментом» с составом гейтов и ролью `task_assigned`/waiver.
   `remember-closeout.instructions.md` п.6: `task_assigned` пишется до работы как единственный
   источник профиля, `--since` обязателен, `--gate-mode`, waiver, команда `audit`.

**Регресс в `--self-test` (+6 проверок: 231 → 237):** CR-1 ×3 — `profile=docs` в `done` не понижает
гейт (профиль из `task_assigned` → block), нет `task_assigned` → отказ в block, нет `task_assigned`
в warn → запись с предупреждением; CR-2 ×2 — `audit` видит decision-waiver → exit 0 / нарушений 0 /
`waiver: 1`, waiver другой задачи не закрывает нарушение; плюс `audit` на отсутствующем журнале →
exit 2.

| Проверка | Результат |
|---|---|
| `python agent-system\tools\journal.py --self-test` | **exit 0**, `SELF-TEST OK (237 checks)` (было 231) |
| `python -m py_compile agent-system\tools\journal.py` | exit 0 |
| `git status --short` | пусто (4 файла закоммичены) |
| `git log --oneline -1` | `56ea9a0` (HEAD → main) |

**Аномалии фикс-раунда CR:** не обнаружено. Правки только в `d:\vscode-data\User\prompts`;
в проекте `library_catalog` изменён лишь этот handoff-файл.

## Фикс-раунд CR-2

- **Дата:** 2026-10-29 | **Коммит:** `0bc1ac3` (репозиторий `d:\vscode-data\User\prompts`, `origin` не настроен — пуш невозможен)
- **Изменённые файлы (4):** `agent-system/tools/journal.py`, `agent-system/session-journal.spec.md`,
  `agent-system/quality-gates.spec.md`, `agent-system/remember-closeout.instructions.md`
  (+173 / −61).
- **Замечание CR (итерация 2, `code-review-T-08.md` §«Итерация 2», Major N1):** `profile` в
  `task_assigned` не был обязательным и не валидировался (опечатка `"featur"` принималась на
  `append`), отсутствовал в строке схемы `session-journal.spec.md:51`, а отказ гейта `done`
  писал «нет события task_assigned», хотя событие есть. Причина и следствие разъезжались:
  агент шёл искать отсутствующее событие.

**Правки:**

1. **`profile` обязателен и валидируется на `append`.** `EVENT_SCHEMA["task_assigned"]["payload"]`
   = `("task", "to", "sp", "profile")` — отсутствие ловится `missing_event_fields` (`exit 1`,
   `отсутствуют обязательные поля: payload.profile`). `EVENT_ENUMS["task_assigned"]` =
   `(("profile", TL2DEV_PROFILES), ("model", TASK_MODELS))` — словарь профилей **не дублируется**:
   взят тот же `TL2DEV_PROFILES`, что и матрица контракта `tl2dev` (один источник, как у
   `NEXT_BY_TYPE`); значение вне словаря → `exit 1` с перечнем допустимых. Дублирующая
   `task_model_problems()` удалена — `model` проверяется тем же `EVENT_ENUMS` (механизм один).
2. **Отказ различает причины.** `journal_profile()` заменена на `journal_profile_state()` →
   `(profile, gap)`, где `gap` — точная причина: «нет события task_assigned» / «событие
   task_assigned есть (ts), но в нём нет поля payload.profile» / «payload.profile='featur' вне
   словаря (допустимо: …)». `gate_gap_text(missing, gap)` и `done_gate_check()` несут `gap`
   вместо булева `confirmed`; `audit` печатает ту же причину в строке `НАРУШЕНИЕ`.
3. **Спека и инструкция.** `session-journal.spec.md:51` — схема `{task, to, sp, profile}`;
   новый абзац «`task_assigned.profile`: обязательное поле…»; в таблицу гейта добавлена строка
   «`task_assigned` есть, но `profile` отсутствует/невалиден» с двумя текстами отказа; пример
   события дополнен `profile`. `remember-closeout.instructions.md` п.6 — явная команда записи
   `task_assigned` с `profile` и ожидаемым отказом без него. `quality-gates.spec.md` §2 —
   «`profile` обязателен и проверяется по `TL2DEV_PROFILES` уже на `append`».

**Регресс в `--self-test` (+7 проверок: 237 → 243), функция `_selftest_task_profile`:**

- `task_assigned` без `profile` → `missing_event_fields` = `["payload.profile"]`;
- словарь профиля в схеме события == `TL2DEV_PROFILES` (один источник);
- `append` без `profile` → `exit 1`, журнал не создан;
- `append` с `profile="featur"` → `exit 1`, названы допустимые значения;
- `journal_profile_state` различает «нет события» / «нет поля profile» / «вне словаря»;
- end-to-end: `task_assigned` без `profile` + полный набор qa/cr/docs + `done --gate-mode block`
  → `exit 1`, в тексте «нет поля payload.profile» и **нет** фразы «нет события task_assigned».

Существующие фикстуры `task_assigned` в `--self-test` дополнены `profile` (иначе они бы падали
на новом обязательном поле); проверка `model='Pro'` переведена на единый механизм `EVENT_ENUMS`.

| Проверка | Результат |
|---|---|
| `python agent-system\tools\journal.py --self-test` | **exit 0**, `SELF-TEST OK (243 checks)` (было 237) |
| `python -m py_compile agent-system\tools\journal.py` | exit 0 |
| зонд A: `task_assigned` без `profile` + qa/cr/docs + `done --gate-mode block` | exit 1, `…не хватает: событие task_assigned есть (2026-10-29T09:00:00), но в нём нет поля payload.profile — профиль не подтверждён…` |
| зонд B: `append task_assigned profile="featur"` | exit 1, `НЕВАЛИДНОЕ событие 'task_assigned': profile='featur' вне словаря (допустимо: feature \| bugfix \| refactoring \| infra \| docs)` |
| зонд C: корректный `profile=feature` + qa/cr/docs + `done --gate-mode block` | `APPENDED: 1 done`, exit 0 |
| зонд D: `profile=None` (поле есть, значение пустое) | exit 1, тот же текст «нет поля payload.profile» |
| `git status --short` (prompts) | пусто (4 файла закоммичены) |
| `git log --oneline -1` (prompts) | `0bc1ac3` (HEAD → main) |

**Аномалии фикс-раунда CR-2:**

1. `git remote` в `d:\vscode-data\User\prompts` по-прежнему отсутствует → пуш коммита `0bc1ac3`
   физически невозможен (как и `8cc10d1`/`56ea9a0`); `origin/main` = локальный `main` проверить нечем.
2. Строгость нового требования — осознанное ужесточение: `append` события `task_assigned` без
   `profile` теперь отказывает (раньше записывалось). Все писатели `task_assigned` в дереве
   промптов (`remember-closeout.instructions.md`, спеки) обновлены; внешние/старые записи в
   боевом журнале не переписываются — гейт на них срабатывает как «профиль не подтверждён»
   (fail-closed), grandfathering по `--since` сохранён.
3. Minor-замечания итерации 1–2 (N2–N6, S5–S10, П-3) не входили в этот фикс-раунд и остались
   в бэклоге; в проекте `library_catalog` изменён только этот handoff-файл.

# Tasks: Topic Suggestions Bot

**Input**: Design documents from `/specs/001-topic-suggestions-bot/`
**Tests**: Required (Constitution III — Test-First). Each test task MUST fail before its implementation task.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [x] T001 Create `pyproject.toml` (Python 3.13, aiogram, groq, aiosqlite, pydantic-settings; dev: pytest, pytest-asyncio) and `.python-version`
- [x] T002 [P] Create `.env.example` with variable names only (per contracts/bot-interface.md)
- [x] T003 [P] Create `bot/__init__.py`, `tests/conftest.py` with fakes (FakeBot, FakeSpeech, FakeSummarizer)

## Phase 2: Foundational

- [x] T004 [P] Test: `tests/test_config.py` — settings load; secrets are `SecretStr` and not in repr
- [x] T005 Implement `bot/config.py`
- [x] T006 [P] Test: `tests/test_storage.py` — add/list/count, kind CHECK, empty text rejected
- [x] T007 Implement `bot/storage.py`
- [x] T008 [P] Implement `bot/texts.py` (Russian strings)

## Phase 3: User Story 1 — Text suggestion (P1) 🎯 MVP

- [x] T009 [US1] Test: `tests/test_handlers_text.py` — text saved then 👍; save error → retry text, no 👍; group chat ignored; /start not saved; sticker → hint
- [x] T010 [US1] Implement text, /start, /whoami, fallback handlers in `bot/handlers.py`
- [x] T011 [US1] Implement `bot/__main__.py` (config, storage, dispatcher DI, polling)

## Phase 4: User Story 2 — Voice suggestion (P2)

- [x] T012 [P] [US2] Test: `tests/test_speech.py` — adapter calls Groq with configured model, returns stripped text
- [x] T013 [US2] Implement `bot/speech.py`
- [x] T014 [US2] Test: `tests/test_handlers_voice.py` — voice transcribed, saved kind=voice, 👍; STT error/empty → retry text, no 👍, nothing saved
- [x] T015 [US2] Implement voice handler in `bot/handlers.py`

## Phase 5: User Story 3 — Author summary (P3)

- [x] T016 [P] [US3] Test: `tests/test_chunking.py` — split ≤4096, no content lost, prefers newline boundaries
- [x] T017 [P] [US3] Test: `tests/test_summary.py` — summarizer builds prompt from all suggestions, uses configured model
- [x] T018 [US3] Implement `bot/summary.py`
- [x] T019 [US3] Test: `tests/test_handlers_summary.py` — author gets chunks; empty → "no suggestions"; non-author refused; LLM error → short error
- [x] T020 [US3] Implement /summary handler in `bot/handlers.py`

## Phase 6: Polish

- [x] T021 Full suite `uv run pytest -q` green; grep code/logs for secret leakage paths
- [ ] T022 Live E2E per quickstart.md (needs real `.env` values from author)
- [x] T023 [P] `README.md` with run instructions (no secrets)

## Phase 7: Codex review fixes (2026-09-16)

- [x] T024 Redact secrets in full formatted log output incl. tracebacks/stack (`bot/redact.py`, `tests/test_redact.py`)
- [x] T025 Reaction failure after persist → "Сохранено ✅" fallback; reply failures never raise (`bot/handlers.py`)
- [x] T026 Map-reduce summary with char budget, item truncation, bounded LLM concurrency (`bot/summary.py`)
- [x] T027 Voice size check before download + STT semaphore (`bot/handlers.py`)
- [x] T028 UNIQUE(chat_id, message_id) + ON CONFLICT DO NOTHING (`bot/storage.py`)
- [x] T029 Suggestions sent to LLM as untrusted JSON data (`bot/summary.py`)
- [x] T030 Timeouts (asyncio + SDK) and SDK retries configured; distinct timeout replies
- [x] T031 `/summary` DB read inside error handling
- [x] T032 SQLite WAL + busy_timeout; DB moved to local disk
- [x] T033 UTF-16 chunking with margin; stop on partial send failure
- [x] T034 Tests: reaction/send failures, commit-before-react order, oversize, concurrency, timeouts, duplicates, traceback redaction
- [x] T035 AsyncExitStack lifecycle; Groq client closed (`bot/__main__.py`)

## Dependencies

Setup → Foundational → US1 → US2 / US3 (US2 and US3 independent after US1's handlers module exists).

<!--
Sync Impact Report
- Version change: template → 1.0.0 (initial ratification)
- Principles added: I. Product Source Is Human-Owned; II. Secrets Never Leave .env;
  III. Test-First; IV. Simplicity; V. Honest Feedback to Users
- Added sections: Technology Constraints, Development Workflow
- Removed sections: none
- Deferred TODOs: none
-->
# Streaming Poll TG Bot Constitution

## Core Principles

### I. Product Source Is Human-Owned
`product.md` is written by the human author and MUST NOT be edited by agents. All specs,
plans and tasks MUST trace back to it; any conflict is resolved in favor of `product.md`
or escalated to the author.

### II. Secrets Never Leave .env (NON-NEGOTIABLE)
The author streams live. Tokens and API keys MUST live only in `.env` (git-ignored) and be
loaded by code at runtime. Agents MUST NOT print, cat, grep or echo `.env` contents. Logs,
exceptions and error messages MUST NOT include secrets or URLs containing them.
`.env.example` lists variable names only.

### III. Test-First
Every behavior change starts with a failing test (red), then the implementation (green).
External services (Telegram, Groq) MUST be mocked at the adapter boundary in unit tests;
at least one live end-to-end check validates the real path before release.

### IV. Simplicity
One process, long polling, single SQLite file, small modules (handlers, storage, speech,
summary, config). No web server, queue or ORM unless a spec requires it.

### V. Honest Feedback to Users
The 👍 reaction means "saved". It MUST only be set after the suggestion is persisted
(and, for voice, successfully transcribed). Failures MUST NOT be acknowledged with 👍.

## Technology Constraints

Python 3.13 managed by `uv`; `aiogram` 3 for Telegram; `groq` SDK for speech-to-text
(whisper-large-v3) and summarization; `aiosqlite` for storage; `pytest` + `pytest-asyncio`.
Model names and IDs come from configuration, never hardcoded in logic.

## Development Workflow

Spec Kit flow: constitution → specify → clarify → plan → tasks → implement. Git default
branch is `master`. Commits happen only with author approval, after the full test suite
passes.

## Governance

This constitution supersedes other practices in this repo. Amendments require author
approval and a semantic version bump (MAJOR: principle removed/redefined; MINOR: principle
or section added; PATCH: wording). Every plan MUST include a Constitution Check.

**Version**: 1.0.0 | **Ratified**: 2026-09-16 | **Last Amended**: 2026-09-16

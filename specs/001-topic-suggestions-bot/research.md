# Research: Topic Suggestions Bot

## Telegram framework
- Decision: aiogram 3 (latest 3.31.0, PyPI checked 2026-09-16), long polling.
- Rationale: async, typed, Router/filters, `bot.set_message_reaction` (Bot API 7.0+) supported.
- Alternatives: python-telegram-bot (heavier, similar); webhooks (need public HTTPS, violates Simplicity).

## Acknowledgement
- Decision: `set_message_reaction(chat_id, message_id, [ReactionTypeEmoji(emoji="👍")])`.
- Rationale: 👍 is in Telegram's allowed default reaction set; bots may react in private chats.

## Speech-to-text
- Decision: Groq `audio.transcriptions.create(model="whisper-large-v3", file=(name, bytes))`,
  model id from config `GROQ_STT_MODEL` (default `whisper-large-v3`, author-chosen).
- Rationale: author choice; accepts Telegram's .ogg/opus directly, no ffmpeg conversion.
- Limits: Groq free-tier upload ≤25 MB — larger/failed → treated as transcription failure.

## Summarization
- Decision: Groq chat completions, model id from required config `GROQ_SUMMARY_MODEL`
  (no hardcoded default in code; `.env.example` suggests a current Groq model).
- Rationale: author choice; model catalog changes, so the id must stay configurable.
- Prompt: Russian; group suggestions into themes with counts, ordered by count.
- Large input: suggestions joined as numbered lines; if over a character budget, truncated per item.

## Config & secrets
- Decision: pydantic-settings reading `.env`; token/key typed `SecretStr`.
- Rationale: `SecretStr` renders as `**********` in repr/logs.
- Author identity: `AUTHOR_USER_ID` (int); `/whoami` replies with the sender's numeric id to help set it.

## Storage
- Decision: aiosqlite, single table, created on startup (`CREATE TABLE IF NOT EXISTS`).
- Alternatives: JSON file (no concurrency safety), Postgres (overkill).

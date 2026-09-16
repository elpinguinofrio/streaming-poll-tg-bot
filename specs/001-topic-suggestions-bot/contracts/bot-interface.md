# Contract: Bot Interface (private chats only)

| Input | Who | Result |
|-------|-----|--------|
| `/start` | anyone | welcome text (how to suggest); not saved |
| `/whoami` | anyone | reply with sender numeric id; not saved |
| `/summary` | author | themed summary, split into ≤4096-char messages; "пока нет предложений" if empty |
| `/summary` | non-author | refusal text; no data revealed |
| text (non-command) | anyone | saved kind=text → 👍 reaction (reaction fails → "Сохранено ✅"); duplicate delivery stored once; on save error → retry text, no 👍 |
| voice | anyone | >19 MiB → "too long"; transcribed → saved kind=voice → 👍; timeout → timeout text; STT/save error or empty transcript → retry text, no 👍 |
| other content | anyone | hint "отправьте текст или голосовое"; not saved |
| any message in group/channel | anyone | ignored |

## Configuration (.env)

| Variable | Required | Notes |
|----------|----------|-------|
| SECRETS_ENV_FILES | no | colon-separated env files with secrets; relative to .env or ~; local .env overrides |
| TELEGRAM_BOT_TOKEN | yes | secret |
| GROQ_API_KEY | yes | secret |
| AUTHOR_USER_ID | no | integer; empty → /summary refused for all (get via /whoami) |
| GROQ_SUMMARY_MODEL | yes | Groq chat model id |
| GROQ_STT_MODEL | no | default whisper-large-v3 |
| DB_PATH | no | default ~/.local/share/streaming-poll-tg-bot/suggestions.db (must be local disk: WAL) |
| GROQ_TIMEOUT_S / GROQ_MAX_RETRIES | no | per-request timeout 20 / SDK retries with backoff+jitter 2 |
| STT_CONCURRENCY / STT_TIMEOUT_S | no | parallel voice downloads+transcriptions 4 / 30 s |
| MAX_VOICE_BYTES | no | 19 MiB; larger → "too long" reply, no download |
| SUMMARY_TIMEOUT_S | no | 90 s (map-reduce over batches) |

# Streaming Poll TG Bot

Telegram bot: viewers DM topic ideas (text or voice), the bot saves them and reacts 👍;
the author gets a notification for every new suggestion and a themed digest with `/summary`.

## Setup
1. Fill `.env` using `.env.example` (never show it on stream). Unknown author id → run bot, DM `/whoami`.
2. The project lives on an SMB share, so keep the venv on local disk:
   `export UV_PROJECT_ENVIRONMENT=$HOME/.cache/venvs/streaming-poll-tg-bot`
3. `uv sync`

Data: SQLite at `~/.local/share/streaming-poll-tg-bot/suggestions.db` (local disk; WAL is unsafe on SMB).

## Run / test
- `uv run python -m bot`
- `uv run pytest -q`

## Commands
`/start` welcome · `/version` version · `/whoami` your Telegram id · `/summary` author-only digest

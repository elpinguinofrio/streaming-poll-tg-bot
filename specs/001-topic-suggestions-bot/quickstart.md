# Quickstart & Validation

## Setup
1. `uv sync`
2. Copy `.env.example` → `.env`, fill values (see [contracts/bot-interface.md](./contracts/bot-interface.md)).
   Never paste `.env` contents on stream.
3. Unknown author id? Start the bot, DM `/whoami`, put the number into `AUTHOR_USER_ID`, restart.

## Tests
`uv run pytest -q` → all pass.

## Run
`uv run python -m bot`

## Manual validation
1. From any account DM a text idea → 👍 appears on it.
2. DM a voice message → 👍 appears; `sqlite3 data/suggestions.db "select kind,text from suggestions"` shows the transcript.
3. Send a sticker → hint reply, no 👍.
4. From the author account `/summary` → themed digest.
5. From another account `/summary` → refusal.

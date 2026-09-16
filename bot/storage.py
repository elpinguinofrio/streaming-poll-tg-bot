import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import aiosqlite

KINDS = ("text", "voice")
BUSY_TIMEOUT_MS = 5000

_SCHEMA = (
    """
    CREATE TABLE IF NOT EXISTS suggestions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        username TEXT,
        kind TEXT NOT NULL CHECK (kind IN ('text', 'voice')),
        text TEXT NOT NULL,
        chat_id INTEGER NOT NULL,
        message_id INTEGER NOT NULL,
        created_at TEXT NOT NULL
    )
    """,
    "CREATE UNIQUE INDEX IF NOT EXISTS suggestions_chat_message ON suggestions (chat_id, message_id)",
)
# Columns added after v0; ensured on open so older databases keep working
_ADDED_COLUMNS = {"voice_path": "TEXT", "voice_file_id": "TEXT", "stt_model": "TEXT"}
_COLUMNS = "id, user_id, username, kind, text, chat_id, message_id, created_at, voice_path, voice_file_id, stt_model"


@dataclass(frozen=True)
class Suggestion:
    id: int
    user_id: int
    username: str | None
    kind: str
    text: str
    chat_id: int
    message_id: int
    created_at: str
    voice_path: str | None = None
    voice_file_id: str | None = None
    stt_model: str | None = None


class Storage:
    """SQLite repository. Keep the file on local disk: WAL does not work on network filesystems."""

    def __init__(self, path: str) -> None:
        self.path = os.path.expanduser(path)
        self._db: aiosqlite.Connection | None = None

    async def open(self) -> None:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._db = await aiosqlite.connect(self.path)
        await self._db.execute(f"PRAGMA busy_timeout = {BUSY_TIMEOUT_MS}")
        await self._db.execute("PRAGMA journal_mode = WAL")
        for statement in _SCHEMA:
            await self._db.execute(statement)
        existing = {row[1] for row in await (await self._db.execute("PRAGMA table_info(suggestions)")).fetchall()}
        for column, column_type in _ADDED_COLUMNS.items():
            if column not in existing:
                await self._db.execute(f"ALTER TABLE suggestions ADD COLUMN {column} {column_type}")
        await self._db.commit()

    async def close(self) -> None:
        if self._db is not None:
            await self._db.close()
            self._db = None

    def _conn(self) -> aiosqlite.Connection:
        if self._db is None:
            raise RuntimeError("storage is not open")
        return self._db

    async def add(self, *, user_id: int, username: str | None, kind: str, text: str,
                  chat_id: int, message_id: int, voice_path: str | None = None,
                  voice_file_id: str | None = None, stt_model: str | None = None) -> int | None:
        """Insert a suggestion; returns its id, or None if this message was already stored."""
        if kind not in KINDS:
            raise ValueError(f"unknown kind: {kind}")
        text = text.strip()
        if not text:
            raise ValueError("empty suggestion text")
        db = self._conn()
        cur = await db.execute(
            "INSERT INTO suggestions (user_id, username, kind, text, chat_id, message_id, created_at,"
            " voice_path, voice_file_id, stt_model) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            " ON CONFLICT (chat_id, message_id) DO NOTHING",
            (user_id, username, kind, text, chat_id, message_id, datetime.now(timezone.utc).isoformat(),
             voice_path, voice_file_id, stt_model),
        )
        await db.commit()
        return cur.lastrowid if cur.rowcount == 1 else None

    async def list_all(self) -> list[Suggestion]:
        cur = await self._conn().execute(
            f"SELECT {_COLUMNS} FROM suggestions ORDER BY id"
        )
        return [Suggestion(*row) for row in await cur.fetchall()]

    async def count(self) -> int:
        cur = await self._conn().execute("SELECT COUNT(*) FROM suggestions")
        (n,) = await cur.fetchone()
        return n

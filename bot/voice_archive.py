import asyncio
import os
import re
from pathlib import Path

_UNSAFE = re.compile(r"[^A-Za-z0-9_-]")


class VoiceArchive:
    """Keeps original voice files on local disk so they can be re-transcribed with another model later."""

    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(os.path.expanduser(str(directory)))

    async def save(self, data: bytes, *, chat_id: int, message_id: int, file_unique_id: str) -> str:
        name = f"{chat_id}_{message_id}_{_UNSAFE.sub('_', file_unique_id)}.ogg"
        return await asyncio.to_thread(self._write, self.directory / name, data)

    @staticmethod
    def _write(path: Path, data: bytes) -> str:
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():  # duplicate delivery of the same message: file already archived
            tmp = path.with_name(f".{path.name}.tmp")
            tmp.write_bytes(data)
            os.replace(tmp, path)
        return str(path)

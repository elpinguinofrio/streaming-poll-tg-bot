import logging
from collections.abc import Iterable

MASK = "***"


class RedactingFormatter(logging.Formatter):
    """Formats the full record (message, exception traceback, stack) and masks secret values."""

    def __init__(self, fmt: str | None = None, *, secrets: Iterable[str], datefmt: str | None = None) -> None:
        super().__init__(fmt, datefmt)
        self._secrets = [s for s in secrets if s]

    def format(self, record: logging.LogRecord) -> str:
        text = super().format(record)
        for secret in self._secrets:
            text = text.replace(secret, MASK)
        return text

import io
import logging

from bot.redact import RedactingFormatter

TOKEN = "123:SECRET"
KEY = "gsk_KEY"


def _logger(name: str) -> tuple[logging.Logger, io.StringIO]:
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(RedactingFormatter("%(levelname)s %(message)s", secrets=[TOKEN, KEY, ""]))
    logger = logging.getLogger(name)
    logger.handlers = [handler]
    logger.propagate = False
    return logger, stream


def test_redacts_message_and_args():
    logger, out = _logger("redact-msg")
    logger.error("url https://api.telegram.org/file/bot123:SECRET/x and %s", KEY)
    text = out.getvalue()
    assert "SECRET" not in text and KEY not in text and "***" in text


def test_redacts_exception_traceback():
    logger, out = _logger("redact-exc")
    try:
        raise RuntimeError(f"Cannot connect: https://api.telegram.org/bot{TOKEN}/getFile")
    except RuntimeError:
        logger.exception("update failed")
    text = out.getvalue()
    assert "Traceback" in text and "RuntimeError" in text
    assert TOKEN not in text and "SECRET" not in text


def test_redacts_stack_info():
    logger, out = _logger("redact-stack")
    secret_local = TOKEN  # noqa: F841 (appears in source line of the stack)
    logger.error("with stack %s", TOKEN, stack_info=True)
    assert TOKEN not in out.getvalue()


def test_plain_text_unchanged():
    logger, out = _logger("redact-plain")
    logger.error("plain text")
    assert out.getvalue() == "ERROR plain text\n"

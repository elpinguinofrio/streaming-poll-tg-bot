import asyncio
import logging
from dataclasses import dataclass
from io import BytesIO
from typing import Protocol

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ReactionTypeEmoji

from bot import texts
from bot.storage import Storage
from bot.summary import split_message, truncate_utf16
from bot.version import get_version

log = logging.getLogger(__name__)

THUMBS_UP = [ReactionTypeEmoji(emoji="👍")]
KIND_ICONS = {"text": "💬", "voice": "🎙"}
NOTIFY_TEXT_LIMIT = 3500  # leaves room for the header within Telegram's 4096 UTF-16 units


@dataclass(frozen=True)
class Limits:
    max_voice_bytes: int = 19 * 1024 * 1024  # Bot API download limit is 20 MB; Groq free tier 25 MB
    stt_concurrency: int = 4
    stt_timeout_s: float = 30.0
    summary_timeout_s: float = 90.0


class Speech(Protocol):
    async def transcribe(self, data: bytes, filename: str) -> str: ...


class Summarizer(Protocol):
    async def summarize(self, texts: list[str]) -> str: ...


def _display_name(message: Message) -> str | None:
    user = message.from_user
    if user is None:
        return None
    return user.username or user.full_name


async def _answer_safely(message: Message, text: str) -> bool:
    try:
        await message.answer(text)
        return True
    except Exception as exc:
        log.error("failed to send reply: %s", type(exc).__name__)
        return False


def _sender_label(message: Message) -> str:
    user = message.from_user
    handle = f"@{user.username}" if user.username else user.full_name
    return f"{handle} (id {user.id})"


async def _notify_author(bot: Bot, author_id: int | None, message: Message, kind: str, text: str) -> None:
    if author_id is None:
        return
    note = texts.NEW_SUGGESTION.format(icon=KIND_ICONS[kind], sender=_sender_label(message),
                                       text=truncate_utf16(text.strip(), NOTIFY_TEXT_LIMIT))
    try:
        await bot.send_message(author_id, note)
    except Exception as exc:
        log.error("failed to notify author: %s", type(exc).__name__)


async def _save_and_ack(message: Message, storage: Storage, kind: str, text: str,
                        bot: Bot, author_id: int | None) -> None:
    try:
        inserted_id = await storage.add(
            user_id=message.from_user.id,
            username=_display_name(message),
            kind=kind,
            text=text,
            chat_id=message.chat.id,
            message_id=message.message_id,
        )  # None means an already-stored duplicate delivery: still persisted, so still acknowledged
    except Exception as exc:  # log type only: messages may carry URLs with secrets
        log.error("failed to save %s suggestion: %s", kind, type(exc).__name__)
        await _answer_safely(message, texts.SAVE_FAILED)
        return
    try:
        await message.react(THUMBS_UP)
    except Exception as exc:
        log.error("failed to set reaction: %s", type(exc).__name__)
        await _answer_safely(message, texts.SAVED_FALLBACK)
    if inserted_id is not None:
        await _notify_author(bot, author_id, message, kind, text)


def create_router(author_id: int | None, limits: Limits) -> Router:
    router = Router(name="suggestions")
    router.message.filter(F.chat.type == ChatType.PRIVATE)
    stt_slots = asyncio.Semaphore(limits.stt_concurrency)

    @router.message(CommandStart())
    async def on_start(message: Message) -> None:
        await _answer_safely(message, texts.WELCOME)

    @router.message(Command("whoami"))
    async def on_whoami(message: Message) -> None:
        await _answer_safely(message, texts.WHOAMI.format(user_id=message.from_user.id))

    @router.message(Command("version"))
    async def on_version(message: Message) -> None:
        version = await asyncio.to_thread(get_version)
        await _answer_safely(message, texts.VERSION.format(version=version))

    @router.message(Command("summary"))
    async def on_summary(message: Message, storage: Storage, summarizer: Summarizer) -> None:
        if author_id is None or message.from_user.id != author_id:
            await _answer_safely(message, texts.NOT_AUTHOR)
            return
        try:
            async with asyncio.timeout(limits.summary_timeout_s):
                items = await storage.list_all()
                summary = await summarizer.summarize([i.text for i in items]) if items else None
        except TimeoutError:
            log.error("summary timed out")
            await _answer_safely(message, texts.SUMMARY_TIMEOUT)
            return
        except Exception as exc:
            log.error("summary failed: %s", type(exc).__name__)
            await _answer_safely(message, texts.SUMMARY_FAILED)
            return
        if not items:
            await _answer_safely(message, texts.NO_SUGGESTIONS)
            return
        for chunk in split_message(summary or texts.SUMMARY_FAILED):
            if not await _answer_safely(message, chunk):
                break

    @router.message(F.text & ~F.text.startswith("/"))
    async def on_text(message: Message, bot: Bot, storage: Storage) -> None:
        await _save_and_ack(message, storage, "text", message.text, bot, author_id)

    @router.message(F.voice)
    async def on_voice(message: Message, bot: Bot, storage: Storage, speech: Speech) -> None:
        size = message.voice.file_size
        if size is not None and size > limits.max_voice_bytes:
            await _answer_safely(message, texts.VOICE_TOO_LARGE)
            return
        try:
            async with stt_slots, asyncio.timeout(limits.stt_timeout_s):
                buffer = await bot.download(message.voice, destination=BytesIO())
                transcript = await speech.transcribe(buffer.getvalue(), "voice.ogg")
        except TimeoutError:
            log.error("voice transcription timed out")
            await _answer_safely(message, texts.VOICE_TIMEOUT)
            return
        except Exception as exc:  # download errors can include the token-bearing file URL
            log.error("voice transcription failed: %s", type(exc).__name__)
            transcript = ""
        if not transcript.strip():
            await _answer_safely(message, texts.VOICE_FAILED)
            return
        await _save_and_ack(message, storage, "voice", transcript, bot, author_id)

    @router.message()
    async def on_other(message: Message) -> None:
        await _answer_safely(message, texts.UNSUPPORTED)

    return router


def create_dispatcher(*, storage: Storage, speech: Speech, summarizer: Summarizer, author_id: int | None,
                      limits: Limits = Limits()) -> Dispatcher:
    dp = Dispatcher()
    dp["storage"] = storage
    dp["speech"] = speech
    dp["summarizer"] = summarizer
    dp.include_router(create_router(author_id, limits))
    return dp

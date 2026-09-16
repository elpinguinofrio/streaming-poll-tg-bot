from aiogram.types import ReactionTypeEmoji

from bot import texts
from bot.handlers import create_dispatcher
from tests.conftest import AUTHOR_ID, FakeSpeech, FakeSummarizer, make_update


def _dp(storage, speech):
    return create_dispatcher(storage=storage, speech=speech, summarizer=FakeSummarizer(), author_id=AUTHOR_ID)


async def test_voice_transcribed_saved_thumbs_up(bot, session, storage):
    speech = FakeSpeech(result="сделай выпуск про роботов")
    await _dp(storage, speech).feed_update(bot, make_update(voice=True, message_id=77))
    assert speech.calls and speech.calls[0][0] == session.file_bytes
    items = await storage.list_all()
    assert [(i.kind, i.text, i.message_id) for i in items] == [("voice", "сделай выпуск про роботов", 77)]
    [reaction] = session.reactions()
    assert reaction.message_id == 77 and reaction.reaction == [ReactionTypeEmoji(emoji="👍")]
    assert session.sent_texts() == []


async def test_voice_stt_error_no_save_no_thumbs(bot, session, storage):
    await _dp(storage, FakeSpeech(error=RuntimeError("boom"))).feed_update(bot, make_update(voice=True))
    assert await storage.count() == 0
    assert session.reactions() == []
    assert session.sent_texts() == [texts.VOICE_FAILED]


async def test_voice_empty_transcript_no_save(bot, session, storage):
    await _dp(storage, FakeSpeech(result="")).feed_update(bot, make_update(voice=True))
    assert await storage.count() == 0
    assert session.reactions() == []
    assert session.sent_texts() == [texts.VOICE_FAILED]


import asyncio

from bot.handlers import Limits


async def test_oversized_voice_rejected_before_download(bot, session, storage):
    speech = FakeSpeech()
    dp = create_dispatcher(storage=storage, speech=speech, summarizer=FakeSummarizer(), author_id=AUTHOR_ID,
                           limits=Limits(max_voice_bytes=1000))
    await dp.feed_update(bot, make_update(voice=True, voice_size=1001))
    assert speech.calls == []
    assert [type(r).__name__ for r in session.requests] == ["SendMessage"]  # no GetFile
    assert session.sent_texts() == [texts.VOICE_TOO_LARGE]
    assert await storage.count() == 0


async def test_voice_concurrency_is_bounded(bot, session, storage):
    speech = FakeSpeech(delay=0.05)
    dp = create_dispatcher(storage=storage, speech=speech, summarizer=FakeSummarizer(), author_id=AUTHOR_ID,
                           limits=Limits(stt_concurrency=2))
    await asyncio.gather(*(dp.feed_update(bot, make_update(voice=True, message_id=i)) for i in range(8)))
    assert speech.max_active == 2
    assert await storage.count() == 8
    assert len(session.reactions()) == 8


async def test_voice_timeout_distinct_reply(bot, session, storage):
    dp = create_dispatcher(storage=storage, speech=FakeSpeech(delay=1), summarizer=FakeSummarizer(),
                           author_id=AUTHOR_ID, limits=Limits(stt_timeout_s=0.05))
    await dp.feed_update(bot, make_update(voice=True))
    assert session.sent_texts() == [texts.VOICE_TIMEOUT]
    assert session.reactions() == [] and await storage.count() == 0


async def test_voice_download_failure(bot, session, storage):
    async def broken_stream(*args, **kwargs):
        raise RuntimeError("download failed")
        yield b""

    session.stream_content = broken_stream
    speech = FakeSpeech()
    await _dp(storage, speech).feed_update(bot, make_update(voice=True))
    assert speech.calls == []
    assert session.sent_texts() == [texts.VOICE_FAILED]
    assert await storage.count() == 0

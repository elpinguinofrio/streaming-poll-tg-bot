from types import SimpleNamespace

from bot.speech import GroqSpeech


class _Transcriptions:
    def __init__(self):
        self.kwargs = None

    async def create(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(text="  привет мир  ")


async def test_transcribe_uses_model_and_strips():
    tr = _Transcriptions()
    client = SimpleNamespace(audio=SimpleNamespace(transcriptions=tr))
    result = await GroqSpeech(client, model="whisper-large-v3").transcribe(b"data", "v.oga")
    assert result == "привет мир"
    assert tr.kwargs["model"] == "whisper-large-v3"
    assert tr.kwargs["file"] == ("v.oga", b"data")

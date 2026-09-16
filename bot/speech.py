from typing import Any


class GroqSpeech:
    def __init__(self, client: Any, model: str) -> None:
        self._client = client
        self._model = model

    @property
    def model(self) -> str:
        return self._model

    async def transcribe(self, data: bytes, filename: str) -> str:
        result = await self._client.audio.transcriptions.create(model=self._model, file=(filename, data))
        return (result.text or "").strip()

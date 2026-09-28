"""Adapter for the Google Gemini generateContent API."""

import httpx2

from server.providers.base import LLMProvider

API_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self, api_key: str, model: str, client: httpx2.AsyncClient | None = None):
        self._api_key = api_key
        self._model = model
        self._client = client or httpx2.AsyncClient()

    async def complete(self, prompt: str) -> str:
        response = await self._client.post(
            API_URL_TEMPLATE.format(model=self._model),
            headers={"x-goog-api-key": self._api_key},
            json={"contents": [{"parts": [{"text": prompt}]}]},
        )
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]

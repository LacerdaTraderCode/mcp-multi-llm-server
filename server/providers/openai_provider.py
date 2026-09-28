"""Adapter for the OpenAI Chat Completions API."""

import httpx2

from server.providers.base import LLMProvider

API_URL = "https://api.openai.com/v1/chat/completions"


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, api_key: str, model: str, client: httpx2.AsyncClient | None = None):
        self._api_key = api_key
        self._model = model
        self._client = client or httpx2.AsyncClient()

    async def complete(self, prompt: str) -> str:
        response = await self._client.post(
            API_URL,
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={
                "model": self._model,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

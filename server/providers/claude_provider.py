"""Adapter for the Anthropic Messages API."""

import httpx2

from server.providers.base import LLMProvider

API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"


class ClaudeProvider(LLMProvider):
    name = "claude"

    def __init__(self, api_key: str, model: str, client: httpx2.AsyncClient | None = None):
        self._api_key = api_key
        self._model = model
        self._client = client or httpx2.AsyncClient()

    async def complete(self, prompt: str) -> str:
        response = await self._client.post(
            API_URL,
            headers={
                "x-api-key": self._api_key,
                "anthropic-version": ANTHROPIC_VERSION,
            },
            json={
                "model": self._model,
                "max_tokens": 512,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        response.raise_for_status()
        return response.json()["content"][0]["text"]

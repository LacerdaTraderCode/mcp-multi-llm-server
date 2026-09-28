"""Shared pytest fixtures for the test suite."""

import httpx2
import pytest

from server.providers.base import LLMProvider


class FakeProvider(LLMProvider):
    def __init__(self, name: str, answer: str | None = None, error: Exception | None = None):
        self.name = name
        self._answer = answer
        self._error = error

    async def complete(self, prompt: str) -> str:
        if self._error is not None:
            raise self._error
        return f"{self._answer} (prompt: {prompt})"


@pytest.fixture
def fake_provider():
    return FakeProvider


def mock_client(handler) -> httpx2.AsyncClient:
    return httpx2.AsyncClient(transport=httpx2.MockTransport(handler))


@pytest.fixture
def build_mock_client():
    return mock_client

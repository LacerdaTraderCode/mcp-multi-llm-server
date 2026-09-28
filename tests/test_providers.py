"""Tests for the provider adapters: each sends its vendor's request shape and parses the reply."""

import json

import httpx2

from server.providers.claude_provider import ClaudeProvider
from server.providers.gemini_provider import GeminiProvider
from server.providers.openai_provider import OpenAIProvider


async def test_claude_provider_sends_a_messages_request_and_returns_the_text(build_mock_client):
    captured = {}

    def handler(request: httpx2.Request) -> httpx2.Response:
        captured["headers"] = request.headers
        captured["body"] = json.loads(request.content)
        return httpx2.Response(
            200, json={"content": [{"type": "text", "text": "Hello from Claude"}]}
        )

    provider = ClaudeProvider(
        api_key="claude-key", model="test-model", client=build_mock_client(handler)
    )

    answer = await provider.complete("Say hello")

    assert answer == "Hello from Claude"
    assert captured["headers"]["x-api-key"] == "claude-key"
    assert captured["body"]["model"] == "test-model"
    assert captured["body"]["messages"] == [{"role": "user", "content": "Say hello"}]


async def test_openai_provider_sends_a_chat_completion_and_returns_the_text(build_mock_client):
    captured = {}

    def handler(request: httpx2.Request) -> httpx2.Response:
        captured["headers"] = request.headers
        captured["body"] = json.loads(request.content)
        return httpx2.Response(
            200, json={"choices": [{"message": {"role": "assistant", "content": "Hello from GPT"}}]}
        )

    provider = OpenAIProvider(
        api_key="openai-key", model="test-model", client=build_mock_client(handler)
    )

    answer = await provider.complete("Say hello")

    assert answer == "Hello from GPT"
    assert captured["headers"]["authorization"] == "Bearer openai-key"
    assert captured["body"]["messages"] == [{"role": "user", "content": "Say hello"}]


async def test_gemini_provider_sends_a_generate_content_request_and_returns_the_text(
    build_mock_client,
):
    captured = {}

    def handler(request: httpx2.Request) -> httpx2.Response:
        captured["url"] = str(request.url)
        captured["headers"] = request.headers
        captured["body"] = json.loads(request.content)
        return httpx2.Response(
            200, json={"candidates": [{"content": {"parts": [{"text": "Hello from Gemini"}]}}]}
        )

    provider = GeminiProvider(
        api_key="gemini-key", model="test-model", client=build_mock_client(handler)
    )

    answer = await provider.complete("Say hello")

    assert answer == "Hello from Gemini"
    assert captured["url"].endswith("/models/test-model:generateContent")
    assert captured["headers"]["x-goog-api-key"] == "gemini-key"
    assert captured["body"]["contents"] == [{"parts": [{"text": "Say hello"}]}]


async def test_a_provider_raises_when_the_api_returns_an_error_status(build_mock_client):
    def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(401, json={"error": "invalid key"})

    provider = OpenAIProvider(
        api_key="bad-key", model="test-model", client=build_mock_client(handler)
    )

    try:
        await provider.complete("Say hello")
    except httpx2.HTTPStatusError as error:
        assert error.response.status_code == 401
    else:
        raise AssertionError("expected HTTPStatusError")

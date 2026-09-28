"""Tests for the multi-provider comparison logic."""

from server.tools.compare_tool import compare_providers


async def test_every_provider_answers_the_same_prompt(fake_provider):
    providers = {
        "claude": fake_provider("claude", answer="A"),
        "openai": fake_provider("openai", answer="B"),
    }

    answers = await compare_providers("Why is the sky blue?", providers)

    assert answers == {
        "claude": "A (prompt: Why is the sky blue?)",
        "openai": "B (prompt: Why is the sky blue?)",
    }


async def test_a_failing_provider_does_not_hide_the_others(fake_provider):
    providers = {
        "claude": fake_provider("claude", answer="A"),
        "openai": fake_provider("openai", error=RuntimeError("rate limited")),
    }

    answers = await compare_providers("hello", providers)

    assert answers["claude"].startswith("A")
    assert answers["openai"] == "error: rate limited"


async def test_no_providers_yields_an_empty_comparison():
    assert await compare_providers("hello", {}) == {}

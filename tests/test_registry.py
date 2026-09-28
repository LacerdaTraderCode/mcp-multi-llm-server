"""Tests for provider discovery from environment variables."""

from server.providers.registry import build_configured_providers


def test_no_keys_means_no_providers():
    assert build_configured_providers({}) == {}


def test_only_providers_with_a_key_are_registered():
    providers = build_configured_providers({"ANTHROPIC_API_KEY": "a", "GEMINI_API_KEY": "g"})

    assert sorted(providers) == ["claude", "gemini"]


def test_all_three_providers_are_registered_when_all_keys_are_present():
    providers = build_configured_providers(
        {"ANTHROPIC_API_KEY": "a", "OPENAI_API_KEY": "o", "GEMINI_API_KEY": "g"}
    )

    assert sorted(providers) == ["claude", "gemini", "openai"]


def test_the_model_can_be_overridden_per_provider():
    providers = build_configured_providers({"OPENAI_API_KEY": "o", "OPENAI_MODEL": "custom-model"})

    assert providers["openai"]._model == "custom-model"

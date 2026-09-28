"""Builds the set of LLM providers that are actually configured through environment variables.

Model names are overridable per provider because vendors retire and rename
models far more often than this adapter layer needs to change.
"""

import os
from collections.abc import Mapping

from server.providers.base import LLMProvider
from server.providers.claude_provider import ClaudeProvider
from server.providers.gemini_provider import GeminiProvider
from server.providers.openai_provider import OpenAIProvider

DEFAULT_CLAUDE_MODEL = "claude-haiku-4-5"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"


def build_configured_providers(environ: Mapping[str, str] | None = None) -> dict[str, LLMProvider]:
    environ = os.environ if environ is None else environ
    providers: dict[str, LLMProvider] = {}

    if anthropic_key := environ.get("ANTHROPIC_API_KEY"):
        model = environ.get("ANTHROPIC_MODEL", DEFAULT_CLAUDE_MODEL)
        providers["claude"] = ClaudeProvider(api_key=anthropic_key, model=model)

    if openai_key := environ.get("OPENAI_API_KEY"):
        model = environ.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
        providers["openai"] = OpenAIProvider(api_key=openai_key, model=model)

    if gemini_key := environ.get("GEMINI_API_KEY"):
        model = environ.get("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
        providers["gemini"] = GeminiProvider(api_key=gemini_key, model=model)

    return providers

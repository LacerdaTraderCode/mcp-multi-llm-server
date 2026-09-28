"""Core logic for comparing answers across LLM providers."""

import asyncio

from server.providers.base import LLMProvider


async def compare_providers(prompt: str, providers: dict[str, LLMProvider]) -> dict[str, str]:
    """Ask every provider the same prompt and collect their answers by provider name.

    A provider that fails contributes its error message instead of aborting the
    comparison: one broken API should never hide the answers of the others.
    """

    async def ask(name: str, provider: LLMProvider) -> tuple[str, str]:
        try:
            return name, await provider.complete(prompt)
        except Exception as error:
            return name, f"error: {error}"

    answers = await asyncio.gather(*(ask(name, provider) for name, provider in providers.items()))
    return dict(answers)

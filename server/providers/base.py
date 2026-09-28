"""Common interface every LLM provider adapter implements."""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    name: str

    @abstractmethod
    async def complete(self, prompt: str) -> str:
        """Send `prompt` to the provider and return the text of its answer."""

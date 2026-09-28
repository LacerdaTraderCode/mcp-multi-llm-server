"""Builds the MCP server and registers every tool it exposes."""

from collections.abc import Callable

import httpx2
from mcp.server.mcpserver import MCPServer

from server.providers.base import LLMProvider
from server.providers.registry import build_configured_providers
from server.tools.compare_tool import compare_providers
from server.tools.page_summary_tool import fetch_url_summary
from server.tools.time_tool import get_current_time

MISSING_KEYS_MESSAGE = (
    "No provider API keys are configured. Set ANTHROPIC_API_KEY, OPENAI_API_KEY, or GEMINI_API_KEY."
)


def create_server(
    http_client: httpx2.AsyncClient | None = None,
    providers_factory: Callable[[], dict[str, LLMProvider]] = build_configured_providers,
) -> MCPServer:
    client = http_client or httpx2.AsyncClient()
    server = MCPServer(
        name="multi-llm-server",
        instructions="Compare LLM providers, read page metadata, and look up the time.",
    )

    @server.tool()
    def current_time(timezone: str) -> str:
        """Return the current date and time in an IANA timezone, e.g. 'America/Sao_Paulo'."""
        return get_current_time(timezone)

    @server.tool()
    async def summarize_url(url: str) -> dict:
        """Fetch a web page and return its title, word count, and a short excerpt."""
        return await fetch_url_summary(url, client)

    @server.tool()
    def list_available_providers() -> list[str]:
        """List the LLM providers that have an API key configured in this environment."""
        return sorted(providers_factory())

    @server.tool()
    async def compare_llm_responses(prompt: str) -> dict:
        """Send the same prompt to every configured LLM provider and return each answer."""
        providers = providers_factory()
        if not providers:
            return {"error": MISSING_KEYS_MESSAGE}
        return await compare_providers(prompt, providers)

    return server


def main() -> None:
    create_server().run()


if __name__ == "__main__":
    main()

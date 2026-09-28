"""Tests that talk to the server through a real MCP client session, not by calling handlers."""

import json

from mcp import Client

from server.main import create_server


async def test_a_client_can_discover_and_call_tools_over_the_protocol(fake_provider):
    server = create_server(
        providers_factory=lambda: {"claude": fake_provider("claude", answer="A")}
    )

    async with Client(server) as client:
        listed = await client.list_tools()
        comparison = await client.call_tool("compare_llm_responses", {"prompt": "hello"})

    assert "compare_llm_responses" in {tool.name for tool in listed.tools}
    assert json.loads(comparison.content[0].text) == {"claude": "A (prompt: hello)"}

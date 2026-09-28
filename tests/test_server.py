"""Tests that the MCP server registers its tools and that they work end to end via call_tool."""

import json

import httpx2
import pytest
from mcp.server.mcpserver.exceptions import ToolError

from server.main import MISSING_KEYS_MESSAGE, create_server


def _json_payload(result) -> dict:
    return json.loads(result.content[0].text)


async def test_the_server_exposes_every_expected_tool():
    server = create_server(providers_factory=dict)

    tool_names = {tool.name for tool in await server.list_tools()}

    assert tool_names == {
        "current_time",
        "summarize_url",
        "list_available_providers",
        "compare_llm_responses",
    }


async def test_current_time_tool_runs_through_the_server():
    server = create_server(providers_factory=dict)

    result = await server.call_tool("current_time", {"timezone": "UTC"})

    assert result.content[0].text.endswith("+00:00")


async def test_current_time_tool_reports_an_error_for_an_unknown_timezone():
    server = create_server(providers_factory=dict)

    with pytest.raises(ToolError):
        await server.call_tool("current_time", {"timezone": "Mars/Olympus_Mons"})


async def test_list_available_providers_reports_only_configured_ones(fake_provider):
    server = create_server(
        providers_factory=lambda: {
            "openai": fake_provider("openai", answer="B"),
            "claude": fake_provider("claude", answer="A"),
        }
    )

    result = await server.call_tool("list_available_providers", {})

    assert result.structured_content == {"result": ["claude", "openai"]}


async def test_compare_reports_missing_keys_instead_of_failing():
    server = create_server(providers_factory=dict)

    result = await server.call_tool("compare_llm_responses", {"prompt": "hello"})

    assert _json_payload(result) == {"error": MISSING_KEYS_MESSAGE}


async def test_compare_returns_each_providers_answer(fake_provider):
    server = create_server(
        providers_factory=lambda: {
            "claude": fake_provider("claude", answer="A"),
            "openai": fake_provider("openai", answer="B"),
        }
    )

    result = await server.call_tool("compare_llm_responses", {"prompt": "hello"})

    assert _json_payload(result) == {
        "claude": "A (prompt: hello)",
        "openai": "B (prompt: hello)",
    }


async def test_summarize_url_tool_uses_the_injected_http_client(build_mock_client):
    client = build_mock_client(
        lambda request: httpx2.Response(200, text="<title>Example</title><p>Hello world</p>")
    )
    server = create_server(http_client=client, providers_factory=dict)

    result = await server.call_tool("summarize_url", {"url": "https://example.com"})

    payload = _json_payload(result)
    assert payload["title"] == "Example"
    assert payload["url"] == "https://example.com"

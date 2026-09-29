# Multi-Provider MCP Server

A [Model Context Protocol](https://modelcontextprotocol.io/) server, built on the official Python SDK, whose headline tool asks the same question to Claude, OpenAI, and Gemini and returns the answers side by side. The provider layer is a small adapter interface, so adding a fourth vendor means adding one file.

## Tools

| Tool | What it does |
|---|---|
| `compare_llm_responses` | Sends one prompt to every configured provider concurrently and returns each answer keyed by provider. A provider that fails reports its error without hiding the others. |
| `list_available_providers` | Lists the providers that have an API key configured. |
| `summarize_url` | Fetches a page and returns its title, word count, and a short excerpt. |
| `current_time` | Returns the current time in any IANA timezone. |

## Design

- **Adapter per vendor.** `LLMProvider` defines a single `complete(prompt)` method. `ClaudeProvider`, `OpenAIProvider`, and `GeminiProvider` each translate that into their vendor's request and response shape.
- **Providers are opt-in.** `build_configured_providers` registers only the vendors whose API key is present in the environment. With no keys set, the comparison tool explains what to configure instead of failing.
- **Logic lives outside the MCP layer.** Each tool is a thin wrapper over a plain function, so the behavior is tested directly and again through a real MCP client session.
- **Injectable dependencies.** `create_server` accepts an HTTP client and a provider factory, which is what lets the test suite run without network access or API keys.

## Running it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...   # set any combination of the three keys
python -m server.main
```

The server speaks MCP over stdio. To use it from an MCP client such as Claude Desktop, register it as a stdio server:

```json
{
  "mcpServers": {
    "multi-llm": {
      "command": "python",
      "args": ["-m", "server.main"],
      "cwd": "/path/to/mcp-multi-llm-server",
      "env": { "ANTHROPIC_API_KEY": "...", "OPENAI_API_KEY": "..." }
    }
  }
}
```

Default models can be overridden with `ANTHROPIC_MODEL`, `OPENAI_MODEL`, and `GEMINI_MODEL`; see `.env.example`.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

The suite mocks the HTTP layer, so it needs no network access and no API keys. It covers each adapter's request and response shape, failure isolation in the comparison, and a full client-to-server round trip over the MCP protocol.

Note that the adapters are verified against mocked responses that follow each vendor's documented API, not against the live services.

## License

MIT — see [LICENSE](LICENSE).

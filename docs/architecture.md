# Architecture

```mermaid
flowchart LR
    Client[MCP client, e.g. Claude Desktop] -- stdio --> Server[MCPServer]
    Server --> Compare[compare_llm_responses]
    Server --> List[list_available_providers]
    Server --> Summary[summarize_url]
    Server --> Time[current_time]
    Compare --> Registry[build_configured_providers]
    Registry --> Claude[ClaudeProvider]
    Registry --> OpenAI[OpenAIProvider]
    Registry --> Gemini[GeminiProvider]
    Summary --> Http[httpx2.AsyncClient]
```

## Layers

**`server/main.py`** builds the `MCPServer` and registers each tool. It contains no business logic; every tool delegates to a plain function.

**`server/tools/`** holds that logic: `compare_providers` fans a prompt out to all providers with `asyncio.gather` and isolates failures, `fetch_url_summary` extracts page metadata, and `get_current_time` resolves an IANA timezone.

**`server/providers/`** holds the adapters. `LLMProvider` is the only thing the comparison logic knows about, which is why a new vendor never touches it.

## Why failures are isolated

The point of comparing providers is to see several answers at once. If one API is rate limited or misconfigured, that provider's slot carries its error message and the rest still return, so a single bad key never turns a comparison into an empty result.

## Testing approach

Adapters are tested with `httpx2.MockTransport`, asserting the exact request each vendor expects and the way its response is parsed. The server is tested twice: by calling registered tools directly, and through `mcp.Client`, which performs a real protocol handshake in memory.

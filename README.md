# Opus 4.7 Tool Agent

Correlation Zero agent that calls Claude Opus 4.7 with tools enabled.

## Enabled Capabilities

- `web_search`: Anthropic server-side `web_search_20260209`
- `web_fetch`: Anthropic server-side `web_fetch_20260209`
- `code_execution`: Anthropic server-side `code_execution_20260120`
- `WebFetch`: local URL fetch with optional Haiku summarization
- `Read`, `Write`, `Edit`, `Glob`, `Grep`: local workspace file operations
- `bash` / `Bash`: Anthropic-schema and custom local non-interactive shell execution
- `Task`: synchronous Anthropic sub-agent call
- `str_replace_based_edit_tool`: Anthropic-schema text editor tool implemented locally
- MCP connector: remote MCP server passthrough through Anthropic `mcp_servers`

## Runtime Contract

- Entry point: `agent.py`
- Agent class: `OpusToolAgent`
- CLI command: `python agent.py`
- Required secret: `ANTHROPIC_API_KEY`
- Optional model override: `ANTHROPIC_MODEL`
- Optional MCP config: `MCP_SERVERS_JSON` or `MCP_SERVER_URL`
- External API: `https://api.anthropic.com/v1/messages`
- Dependency: `certifi`

## MCP Configuration

Use `MCP_SERVERS_JSON` for one or more remote MCP servers:

```json
[
  {
    "type": "url",
    "name": "example-mcp",
    "url": "https://example.com/sse",
    "authorization_token": "optional-token"
  }
]
```

Or configure one server with:

```bash
MCP_SERVER_URL="https://example.com/sse"
MCP_SERVER_NAME="example-mcp"
MCP_AUTH_TOKEN="optional-token"
```

## Quickstart

```bash
./tools/test_agent.sh
./tools/prepare_submission.sh
```

For local live calls, set `.env.local`:

```bash
ANTHROPIC_API_KEY="..."
ANTHROPIC_MODEL="claude-opus-4-7"
ANTHROPIC_TIMEOUT_SECONDS="20"
ANTHROPIC_TOTAL_TIMEOUT_SECONDS="27"
```

# Apohara PROBANT — MCP Server

Apohara PROBANT exposes its verification pipeline as an [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server. Any MCP-capable client — Claude Desktop, Claude Code, Cursor, Zed — can call the verification tools directly without leaving the editor.

## What is the Apohara MCP server?

A Python implementation of the MCP `stdio` protocol. It wraps the three core PROBANT API endpoints as callable tools and routes them to `https://api.apohara.dev` (or a local backend).

The server is defined in `packages/backend/mcp_server.py` using the [`mcp`](https://pypi.org/project/mcp/) Python library. Wire protocol is `stdio`; the client spawns the process and talks JSON-RPC over stdin/stdout.

## Tools exposed

| Tool | Signature | Description |
|---|---|---|
| `verify_code` | `code: str, gemini_api_key?: str` | Verify AI-generated code with the 9-vendor adversarial ensemble. Returns a `verdict` (`verified` / `risky` / `blocked`), per-attacker reasoning, and a `signed_hash` for audit lookup. If `gemini_api_key` is omitted, the shared demo quota applies (5 requests/IP/day). |
| `get_audit` | `verdict_id: str` | Fetch a previously signed verdict from the SHA-256 + HMAC ledger by its `signed_hash`. |
| `list_recent_verdicts` | `limit?: int (default 20)` | List the most recent N audit ledger entries. Requires `APOHARA_ADMIN_KEY` environment variable on the backend. |

## Install

> **Not yet on PyPI.** Install from source for now:

```bash
pip install -e packages/backend
pip install mcp httpx
```

When published:

```bash
pip install apohara-probant-mcp
```

## Configure in Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "apohara-probant": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/path/to/apohara-inti/packages/backend",
      "env": {
        "APOHARA_PROBANT_API": "https://api.apohara.dev"
      }
    }
  }
}
```

## Configure in Cursor

In `.cursor/mcp.json` at your project root (or global Cursor settings):

```json
{
  "mcpServers": {
    "apohara-probant": {
      "command": "python",
      "args": ["/path/to/apohara-inti/packages/backend/mcp_server.py"],
      "env": {
        "APOHARA_PROBANT_API": "https://api.apohara.dev"
      }
    }
  }
}
```

## Configure in Claude Code

```bash
# Add to your project's .claude/settings.json mcpServers block, or run:
claude mcp add apohara-probant python -- -m mcp_server
```

See [integration-examples/claude-code.md](integration-examples/claude-code.md) for the full snippet.

## Run standalone for debugging

```bash
cd packages/backend
APOHARA_PROBANT_API=https://api.apohara.dev python mcp_server.py
```

The server prints nothing to stdout when healthy (stdout is the MCP wire). Errors go to stderr.

## License

Apache-2.0 — see [LICENSE](../../LICENSE).

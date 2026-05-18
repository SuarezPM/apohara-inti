# Apohara PROBANT MCP Server — Specification

## Wire protocol

- **Transport**: `stdio` (MCP standard). The client launches `python mcp_server.py` as a subprocess and communicates via JSON-RPC 2.0 over stdin/stdout.
- **No HTTP port is opened**. All network I/O goes through the backend API at `APOHARA_PROBANT_API` (default: `https://api.apohara.dev`).

## Tool schemas

### `verify_code`

```json
{
  "name": "verify_code",
  "description": "Verify AI-generated code with the 9-vendor adversarial ensemble.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "code": {
        "type": "string",
        "description": "Code or task to verify"
      },
      "gemini_api_key": {
        "type": "string",
        "description": "Optional BYOK Gemini key. If absent, uses shared demo quota."
      }
    },
    "required": ["code"]
  }
}
```

**Response** (JSON string): `VerifyResponse` from `/v1/verify` or `/v1/demo_verify`:

```json
{
  "verdict": "verified | risky | blocked",
  "attackers": [
    { "vendor": "openai", "model": "gpt-4o", "found_issue": false, "reasoning": "..." }
  ],
  "memory_isolation": { "inv15_enforced": true, "contextforge_audit_id": "<uuid>" },
  "signed_hash": "<sha256-hex>",
  "latency_ms": 2341.7,
  "cost_estimate_usd": 0.004821,
  "cost_capped": false
}
```

### `get_audit`

```json
{
  "name": "get_audit",
  "description": "Fetch a previously signed verdict from the SHA-256 + HMAC ledger.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "verdict_id": {
        "type": "string",
        "description": "signed_hash from a prior verify call"
      }
    },
    "required": ["verdict_id"]
  }
}
```

**Response**: the raw ledger JSON object (same as `GET /v1/audit/{verdict_id}`).

### `list_recent_verdicts`

```json
{
  "name": "list_recent_verdicts",
  "description": "List the most recent N audit ledger entries (admin-only when wired).",
  "inputSchema": {
    "type": "object",
    "properties": {
      "limit": { "type": "integer", "default": 20 }
    }
  }
}
```

**Response**: `{ "entries": [...], "limit": N, "total_returned": N }` from `GET /v1/audit/recent`.

## Error responses

The server wraps backend HTTP errors as MCP `TextContent` with a JSON body:

```json
{ "error": "HTTP 401: Gemini API key rejected" }
{ "error": "HTTP 404: no ledger entry for <hash>" }
{ "error": "list_recent_verdicts requires /v1/audit/recent endpoint" }
```

On a network failure, `httpx.HTTPError` is caught and surfaced similarly.

## Authentication

- **`verify_code` with BYOK key**: the Gemini API key is passed as the `gemini_api_key` tool argument. It is forwarded to `POST /v1/verify`. The MCP client stores the key however it handles secrets (environment variable injection recommended).
- **`verify_code` without key**: routes to `POST /v1/demo_verify`. The backend's `DEMO_GEMINI_KEY` is used server-side. No credential leaves the client.
- **`list_recent_verdicts`**: set `APOHARA_ADMIN_KEY` in the MCP server process env (via `"env"` in the client config). The server passes it as a query parameter to `GET /v1/audit/recent?admin_key=<key>`.

## Rate limiting

- Demo path (`verify_code` without BYOK key): inherits `/v1/demo_verify`'s 5 requests/IP/day limit. The backend enforces this; the MCP server surfaces `HTTP 429` as an error string.
- BYOK path: no additional rate limit at the MCP layer. Backend cost ceiling (`$0.50/call`) still applies.

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `APOHARA_PROBANT_API` | `https://api.apohara.dev` | Backend base URL |
| `APOHARA_ADMIN_KEY` | _(empty)_ | Forwarded to `/v1/audit/recent` for admin access |

## Dependency

The server requires `mcp>=1.0` and `httpx>=0.27`. Install:

```bash
pip install mcp httpx
```

If `mcp` is absent, the process prints an error to stderr and exits with code 1.

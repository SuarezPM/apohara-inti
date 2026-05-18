# Cursor — Apohara PROBANT MCP Integration

## Config snippet

Create `.cursor/mcp.json` at your project root (or add to Cursor global settings):

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

Restart Cursor after saving. The MCP panel should show `apohara-probant` as connected.

## Sample usage

In the Cursor Agent chat:

```
@apohara-probant verify_code: "SELECT * FROM orders WHERE id = " + userId
```

Or with a BYOK Gemini key (prevents shared-quota exhaustion):

```
@apohara-probant verify_code code="..." gemini_api_key="AIza..."
```

The tool returns the full verdict JSON including `signed_hash`, which you can pass to `get_audit` to retrieve the ledger entry later.

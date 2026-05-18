# Zed — Apohara PROBANT MCP Integration

## Config snippet

In Zed settings (`~/.config/zed/settings.json`), add:

```json
{
  "context_servers": {
    "apohara-probant": {
      "command": {
        "path": "python",
        "args": ["/path/to/apohara-inti/packages/backend/mcp_server.py"],
        "env": {
          "APOHARA_PROBANT_API": "https://api.apohara.dev"
        }
      }
    }
  }
}
```

Zed uses `context_servers` as the MCP server key (as of Zed 0.140+). Restart Zed after saving.

## Sample usage

Open the Assistant panel (`Ctrl+?`). The `verify_code`, `get_audit`, and `list_recent_verdicts` tools appear in the tool picker. Select `verify_code`, paste your code, and submit. The verdict and attacker breakdown render inline in the conversation thread.

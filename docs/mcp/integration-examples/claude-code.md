# Claude Code — Apohara PROBANT MCP Integration

## Config snippet

Add to your project's `.claude/settings.json`:

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

Or register globally via CLI:

```bash
claude mcp add apohara-probant python -- -m mcp_server \
  --cwd /path/to/apohara-inti/packages/backend
```

## Sample usage

Once registered, Claude Code can call the tools inline during a session:

```
Use the verify_code tool to check the following Python snippet for vulnerabilities:

def run_query(user_input):
    return db.execute(f"SELECT * FROM users WHERE id = {user_input}")
```

Claude Code will call `verify_code` with the snippet, display the verdict, attacker reasoning, and `signed_hash` directly in the conversation.

To look up a previous result:

```
Call get_audit with verdict_id = "a3f9d2c1..."
```

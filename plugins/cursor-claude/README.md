# Apohara PROBANT — Cross-AI Verifier for Cursor / VS Code

Verify AI-generated code against a **9-vendor adversarial ensemble** before you merge. Each verification call dispatches your code to multiple attacker models; a signed verdict is returned with per-vendor reasoning, latency, and cost estimate.

## Install

1. Build the `.vsix` package (requires Node.js + `vsce`):
   ```bash
   npm install
   npm run package
   ```
2. In Cursor (or VS Code): open the **Extensions** sidebar, click the `...` menu, choose **Install from VSIX...**, and select the generated `.vsix` file.

## Configure

Open Settings (`Cmd+,` / `Ctrl+,`) and search for **Apohara**:

| Setting | Default | Description |
|---|---|---|
| `apohara.apiUrl` | `https://api.apohara.dev` | PROBANT backend URL |
| `apohara.geminiApiKey` | _(empty)_ | Your Gemini API key (BYOK). Get one at [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |

Leave `geminiApiKey` empty to use the shared demo quota (`/v1/demo_verify`, 5 calls/IP/day).

## Use

Open the Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`) and run:

- **Apohara: Verify Current Diff** — verifies `git diff HEAD` in the current workspace root.
- **Apohara: Verify Selection** — verifies whatever code you have highlighted in the active editor.

## Output

A toast notification shows the verdict at a glance:

- `✓ VERIFIED` — no attacker flagged an issue
- `⚠ RISKY` — one or more attackers raised a concern
- `✕ BLOCKED` — majority of attackers flagged a critical issue

The **Apohara PROBANT** output channel (View > Output) shows the full per-vendor breakdown with reasoning and the signed `HMAC` hash for audit trail.

## License

Apache-2.0. See [LICENSE](./LICENSE).

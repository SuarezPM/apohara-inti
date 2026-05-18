# Submission Video Script — Apohara PROBANT
**Target length:** 3–5 minutes  
**Recording notes:** You know your setup. This script is content-only. Timestamps are targets, not hard cuts.

---

## 0:00 — 0:30 Cold open

**[On camera — direct address, no screen yet]**

"Your AI writes code. A different AI reviews it. But who reviews *that* AI?"

Beat.

"Apohara PROBANT sends every AI-generated output through 12 independent frontier
vendors — each isolated so they cannot contaminate each other's reasoning.
Not claimed. Measured. Formally proven."

**[Cut to: apohara.dev hero in browser — full screen]**

---

## 0:30 — 1:30 Live demo — SQLi attack path

**[Browser: apohara.dev — TryItPanel visible]**

Voice-over while typing:

"First: the attacker path. I paste a SQL injection payload."

Type in the input field:
```
SELECT * FROM users WHERE 1=1; --
```

Click Verify.

"LobsterTrap DPI intercepts before the payload reaches Gemini or any vendor."

**[Timer visible on screen — aim for the ~25 ms verdict timestamp]**

"Verdict: blocked. 25 milliseconds. Zero LLM tokens consumed. Zero cost."

Scroll down to show the audit ledger entry — click `/v1/audit/<hash>`.

"Every verdict is HMAC-SHA256 signed. This chain entry cannot be forged.
`verify_chain()` re-derives it independently."

Voice-over:

"Measured block rate: 50% on SQL injection payloads, n=20, Wilson CI
29.9% to 70.1% — directional. Benign false-positive rate: 9.8%, n=51.
Those numbers are in `logs/lobstertrap_block_rate_*.json` in the repo.
Not hand-picked. Auditable."

---

## 1:30 — 2:30 Benign code — 12-vendor ensemble streams in

**[Browser: clear input field, paste a real function]**

Paste something like:
```python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)
```

Toggle stream mode on. Click Verify.

**[Watch the per-vendor cards resolve in real-time as SSE events arrive]**

Voice-over while cards populate:

"Stream mode. Each vendor publishes its verdict the moment it completes —
no polling, no waiting for the slowest model to finish."

Wait for final verdict to appear.

"12 frontier vendors. Aggregation rule is transparent: 0-2 harmful votes =
verified, 3-5 = risky, 6 or more = blocked. No black box."

Point at the cost and latency readout.

"Cost and latency displayed per call. p50 around 30 seconds for a full
12-vendor pass. Cost ceiling is $0.50 per call."

---

## 2:30 — 3:30 Repo tour — research credentials

**[Switch to browser tab: github.com/SuarezPM/apohara-inti]**

Navigate to `logs/` directory.

"Everything I just showed has a backing log file. Click any of these."

Click `baseline_aegis-ensemble-10frontier_day5_FALLBACK_20260515T212737Z.json`.

"JBB-Behaviors holdout set, n=80. Block rate 93.75%. Wilson 95% confidence
interval: 86.2% to 97.3%. The CI bounds are in the file. We report the
honest width, not just the point estimate."

Navigate to the paper DOI link or type: `doi.org/10.5281/zenodo.20114594`

**[Zenodo deposit page visible]**

"INV-15 paper. Version 2.0.1 is on Zenodo. Version 3.0 adds a Z3 SMT
formal proof — the negation of INV-15 is mathematically unsatisfiable.
Checked by Z3 in 10.08 milliseconds on AMD MI300X."

Beat.

"Every claim in our repo cites a log file or a paper. If we can't cite it,
we don't claim it. AUDIT.md lists 10 overclaims from the previous version
and how each one was closed."

---

## 3:30 — 4:30 Distribution channels

**[Switch to: VS Code or Cursor with extension installed]**

"The Cursor plugin ships as a VSIX today."

Show the extension installed in Cursor sidebar. Run `Apohara: Verify Selection`
on a code snippet. Show the output panel response.

"BYOK — bring your own API key. Apache-2.0. Install from
`plugins/cursor-claude/apohara-probant-verify-0.1.0.vsix`."

**[Switch to: apohara.dev/dashboard]**

"Ops dashboard at `/dashboard`. Rolling verdict history, block rate trend,
cost per call."

**[Switch to: terminal or editor — show mcp_server.py config snippet]**

"MCP server for Claude Desktop, Cursor, Zed — three tools exposed:
`verify_code`, `get_audit`, `list_recent_verdicts`. Stdio transport, drop
the server block into your MCP config and you're running."

---

## 4:30 — 5:00 Close

**[Back to apohara.dev — hero screen. Stay wide.]**

Voice-over:

"Apohara PROBANT. 12-vendor adversarial AI verifier.
Formally proven INV-15 KV-cache isolation.
128 tests passing. 15-plus measurement logs committed to repo.
Apache-2.0."

Pause.

"github.com/SuarezPM/apohara-inti"

**[Hold on wordmark / shield logo]**

"Built by Pablo M. Suarez. If you have questions — GitHub issues or the
contact on the site."

Fade out.

---

## B-roll / cutaway notes

- The LobsterTrap 25 ms timer hit is the strongest visual. If it's slow on
  recording day, note in voice-over that the demo endpoint is under load and
  cut to a pre-recorded capture.
- The streaming SSE card animation is visually distinct from all competitors —
  linger on it for a full 10–15 seconds so judges internalize it.
- Do not show competitor names on screen. The contrast is implicit.

## Mandatory overlays / lower thirds

| Timestamp | Text |
|-----------|------|
| 0:30 | "LobsterTrap DPI — pre-LLM interception" |
| 1:00 | "50% SQLi block · 9.8% FPR · logs/ in repo" |
| 1:30 | "12 vendors · SSE streaming · INV-15 isolated" |
| 2:30 | "JBB block rate 93.75% · Wilson CI [86.2%, 97.3%]" |
| 3:00 | "Z3 SMT formal proof · UNSAT in 10.08 ms" |
| 3:30 | "Cursor VSIX · MCP server · /dashboard · Apache-2.0" |
| 4:30 | "github.com/SuarezPM/apohara-inti · Pablo M. Suarez" |

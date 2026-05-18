# Pablo Handoff — Submission freeze actions (T+5:09)

> **DECISION BRANCH RESOLVED**: ship **`.9vendor.md` variants** (droplet runs 9-vendor; SSH stuck so 12-vendor upgrade deferred to post-hackathon).
>
> Sections below are copy-paste ready for manual execution at T+5:09 FREEZE.
>
> Each section starts with a hold instruction. Exception: video recording (you pace yourself).
>
> **Confirmed live URLs (smoke 2026-05-18 19:09 UTC, log `logs/techex_submission_smoke_20260518T190917Z.json`)**:
> - ✅ https://www.apohara.dev (HTTP/2 200)
> - ✅ https://api.apohara.dev/health (200)
> - ✅ https://apohara-nextjs.vercel.app (SSR PoC, 200)
> - ✅ https://github.com/SuarezPM/apohara-probant (200)
> - ✅ https://github.com/SuarezPM/apohara-aegis (200)
> - ✅ https://github.com/SuarezPM/Apohara_Context_Forge (200)
> - ✅ https://github.com/SuarezPM/Apohara-Guard (200, new — public push commit `2502072`)
> - ⚠️ `/v1/demo_verify` is timing out — Gemini key likely exhausted; judges using **BYOK on `/v1/verify`** still works. **Mention "BYOK demo, 5 free/IP/day"** in the submission if asked.

---

## Section 1 — lablab.ai paste: TechEx 2026 submission

**DO NOT START BEFORE T+5:09** unless ralph lead explicitly green-lights early start.

### Step-by-step

1. Open https://lablab.ai in a browser where you are already logged in.
2. Navigate to the TechEx 2026 hackathon page. URL pattern: `https://lablab.ai/event/techex-2026` (check lablab.ai event listing if this 404s — the slug may differ).
3. Click **"Submit project"** (blue button, top-right of the event page).
4. Fill each form field using the source file:

   **Source file:** `docs/submissions/techex-2026-submission.9vendor.md` (decision branch resolved per header)

   | Form field | Where to find it in the .md | Paste exactly |
   |---|---|---|
   | **Project name** | `## Field: Project name` code block | `Apohara PROBANT — Cross-AI Code Verifier` |
   | **Tagline** | `## Field: Tagline` code block | The single line inside the code block (≤80 chars) |
   | **Short pitch** | `## Field: Short pitch` code block | The single paragraph inside the code block (≤200 chars) |
   | **Long description** | `## Field: Long description` code block | The full multi-line block (≤2000 chars) |
   | **Demo URL** | `## Field: Demo URL` code block | `https://www.apohara.dev` |
   | **GitHub URL** | `## Field: GitHub repo URL(s)` code block | Paste all four lines (one per repo) |
   | **Video URL** | `## Field: Video URL` | Paste the YouTube unlisted URL you recorded in Section 4 |
   | **Category tags** | `## Category tags` code block | Select matching tags from lablab.ai's dropdown; match as many as available |

5. Upload a screenshot or logo if the form has an "Image" field. Use the Apohara shield logo if available, or a screenshot of `https://www.apohara.dev`.
6. Click **Save / Submit**.
7. Copy the submission confirmation URL and save it — the ralph lead needs it.

### Character limits — check before pasting

Open a terminal and run:
```bash
# Tagline
wc -m <<'EOF'
A different AI audits the code your AI just wrote. 9-vendor ensemble · INV-15 isolated.
EOF

# Short pitch (paste the actual text from your chosen variant)
# Long description — must be ≤2000 chars; the file was written to fit
```

---

## Section 2 — lablab.ai paste: Milan AI Week 2026 submission

**DO NOT START BEFORE T+5:09** unless ralph lead explicitly green-lights early start.

### Step-by-step

1. Stay logged into lablab.ai (same session as Section 1).
2. Navigate to the Milan AI Week 2026 hackathon page. URL pattern: `https://lablab.ai/event/milan-aiweek-2026` (check event listing if 404).
3. Click **"Submit project"**.
4. Fill each form field using the source file:

   **Source file:** `docs/submissions/milan-aiweek-2026-submission.9vendor.md` (decision branch resolved per header)

   | Form field | Where to find it in the .md | Paste exactly |
   |---|---|---|
   | **Project name** | `## Field: Project name` code block | `Apohara PROBANT — Cross-AI Code Verifier` |
   | **Tagline** | `## Field: Tagline` code block | The single line inside the code block |
   | **Short pitch** | `## Field: Short pitch` code block | The single paragraph inside the code block |
   | **Long description** | `## Field: Long description` code block | The full multi-line block |
   | **Demo URL** | `## Field: Demo URL` code block | `https://www.apohara.dev` |
   | **GitHub URL** | `## Field: GitHub repo URL(s)` code block | All four repo lines |
   | **Video URL** | `## Field: Video URL` | Same YouTube URL as Section 1 (reuse the video) |
   | **Category tags** | `## Category tags` code block | Agent Bench, Multi-Agent, LLM Security, Formal Methods, Open Source, EU AI Act, Benchmark Reproducibility, Adversarial Validation |

5. If the form has a "Track" selector, choose **Agent Bench** (primary).
6. Click **Save / Submit**.
7. Copy the Milan submission confirmation URL and save it.

### Note
Both submissions use the same video. Record once (Section 4 below), upload to YouTube unlisted, paste the same URL in both forms.

---

## Section 3 — Zenodo upload: Paper v3.0

**DO NOT START BEFORE T+5:09** unless ralph lead explicitly green-lights early start.

### Files needed

- PDF: `/home/linconx/Documentos/Apohara_Context_Forge/paper/inv15_paper.pdf` (422 KiB, rebuilt 2026-05-18)
- Metadata reference: `/home/linconx/Documentos/Apohara_Context_Forge/paper/zenodo-v3-metadata.json`

### Step-by-step

1. Open https://zenodo.org in a browser where you are logged in as the Apohara account.
2. Go to https://zenodo.org/uploads/new.
3. Click **"New upload"**.
4. In the upload form:
   - **Communities**: search for "Apohara" — join or select if the community exists. If not, skip.
   - **Upload type**: select "Publication" → "Preprint".
5. Under **"Related/alternate identifiers"**, add:
   - Relation: `isNewVersionOf`
   - Identifier: `10.5281/zenodo.20114594`
   - This links v3.0 to the published v2.0.1.
6. Drag and drop the PDF file:
   `/home/linconx/Documentos/Apohara_Context_Forge/paper/inv15_paper.pdf`
7. Fill metadata fields from `zenodo-v3-metadata.json`:

   | Zenodo field | Value |
   |---|---|
   | **Title** | `INV-15: A formal safety invariant for multi-agent KV-cache isolation (v3.0)` |
   | **Version** | `3.0` |
   | **Publication date** | `2026-05-18` |
   | **Authors** | `Suarez, Pablo M. · Universidad Nacional de Tucumán` |
   | **Description** | `v3.0 adds formal Z3 SMT verification of INV-15 (proof: UNSAT on negation in 10.08 ms) to complement the empirical 0/1210 sweep from v2.0.1. Z3 model fidelity verified line-by-line against the production JCRSafetyGate. v2.0.1 (DOI 10.5281/zenodo.20114594) is the predecessor.` |
   | **License** | `CC-BY-4.0` |
   | **Keywords** | `AI safety, formal verification, Z3 SMT, multi-agent systems, KV cache, INV-15` |

8. Click **"Publish"**.
9. Copy the new DOI assigned to v3.0. It will be a new `10.5281/zenodo.NNNNNNNNN` identifier (different from v2.0.1's `10.5281/zenodo.20114594`). Save it — the ralph lead will update the submission forms and paper if time allows.

### Important
Do not delete or modify the v2.0.1 deposit. The `isNewVersionOf` relation preserves both versions. Zenodo will auto-link them in the version history.

---

## Section 4 — Video recording and upload

> **You pace this section.** Record whenever ready, before T+5:09. No hold needed.
> The only dependency: the submission forms (Sections 1 and 2) need the YouTube URL, so finish recording before you start those.

### Script location

`/home/linconx/Documentos/apohara-inti/docs/video/SUBMISSION-VIDEO-SCRIPT.md`

865 words, 5 scenes, ~3–5 min runtime. You have YouTuber background — follow the script for content, your own pace for delivery.

### Scene summary

| Time | Scene | Key visual |
|---|---|---|
| 0:00–0:30 | Cold open — on camera | "A different AI audits the code your AI just wrote." |
| 0:30–1:30 | Live demo — SQLi attack | LobsterTrap ~25 ms block, HMAC audit ledger |
| 1:30–2:30 | Benign code — SSE streaming | 9 vendor cards resolve in real time |
| 2:30–3:30 | Repo tour — research credentials | logs/ directory, JBB JSON, Zenodo DOI page |
| 3:30–4:30 | Distribution channels | Cursor VSIX, /dashboard, MCP config |
| 4:30–5:00 | Close | `github.com/SuarezPM/apohara-probant` hold (formerly `apohara-inti`) |

### Mandatory on-screen overlays (see script for timestamps)

`LobsterTrap DPI — pre-LLM interception` · `50% SQLi block · 9.8% FPR · logs/ in repo` · `9 vendors · SSE streaming · INV-15 isolated` · `JBB block rate 93.75% · Wilson CI [86.2%, 97.3%]` · `Z3 SMT formal proof · UNSAT in 10.08 ms` · `Cursor VSIX · MCP server · /dashboard · Apache-2.0` · `github.com/SuarezPM/apohara-probant · Pablo M. Suarez`

(Decision branch resolved to **9-vendor staged**: keep "9 vendors" in overlays. The 12-vendor adapter expansion is documented in submission long-desc as "expansion staged in apohara-aegis main; production upgrade deferred to next deploy cycle" — honest framing.)

### Upload

1. Upload to **YouTube as Unlisted** (fastest; no re-upload per platform needed).
2. Copy the unlisted URL (`https://youtu.be/...`).
3. Paste it as the **Video URL** field in both the TechEx and Milan submission forms.

### Fallback
If the LobsterTrap ~25 ms timer runs slow on recording day, note in voice-over that the endpoint is under load, then cut to a pre-recorded capture if you have one. Do not re-record the full video for one slow widget.

# Deploy Apohara Inti behind TerraFabric + Lobster Trap

> docker-compose recipe for running Apohara Inti behind Veea's Lobster
> Trap DPI proxy with a mock VeeaONE control plane stub. Demonstrates
> the integration pattern for a real TerraFabric production deployment
> ([Veea TerraFabric announcement, MWC 2026][tf-mwc]).

---

## Architecture

```
                                ┌──────────────────────────────────┐
                                │  VeeaONE control plane (stub)    │
                                │  :9000 — /healthz /devices       │
                                │         /policies                │
                                └──────────────────────────────────┘
                                         ▲   side-car
                                         │   policy / device sync
                                         │
   user ─HTTP──>  ┌──────────────────────────────────────────┐
       :8080      │  lobster-trap (Veea DPI reverse proxy)   │
                  │  - ingress regex DPI                     │
                  │  - egress regex DPI                      │
                  │  - audit log → stderr / file             │
                  │  - dashboard at /_lobstertrap/           │
                  └──────────────────────────────────────────┘
                            │  proxy_pass to backend
                            ▼
              ┌────────────────────────────────────────────┐
              │  aegis-backend (FastAPI, /v1/verify)       │
              │  - Gemini writer (user BYOK API key)       │
              │  - 9 attacker vendors via apohara-aegis    │
              │  - INV-15 gate via apohara-context-forge   │
              │  - signed SHA-256 ledger                   │
              └────────────────────────────────────────────┘
                            │  in-process import
                            ▼
              ┌────────────────────────────────────────────┐
              │  contextforge-sidecar (FastAPI MCP)        │
              │  - JCRSafetyGate (INV-15)                  │
              │  - ContextRegistry (LSH + FAISS)           │
              │  - exposed at :8001 for future remote use  │
              └────────────────────────────────────────────┘
```

The backend currently imports `apohara_context_forge` directly in-process
(see `packages/backend/main.py:60`). The sidecar at port 8001 is still
spun up so that a future US-010+ change can flip to over-the-wire MCP
calls without touching this compose file.

---

## Required env vars

Apohara Inti routes the 9 attacker vendors via shared aggregators (mostly
OpenRouter + opencode Zen), so you only need to set the upstream-aggregator
keys, not every model's vendor key. Set these in your shell before running
`docker-compose up`, or use an `.env` file in this directory:

| Env var | Purpose | Required for |
|---|---|---|
| `OPENROUTER_API_KEY` | Aggregator that fronts Claude, GPT, DeepSeek seats | Most of the 9-attacker grid |
| `OPENCODE_ZEN_API_KEY` | opencode Zen attackers (Codex, Grok) | 2 of 9 attacker seats |
| `MINIMAX_API_KEY` | MiniMax M2.7 direct | 1 of 9 attacker seats |
| `NVIDIA_API_KEY` | Nemotron via NVIDIA NIM endpoint | 1 of 9 attacker seats |
| `GEMINI_API_KEY` | The user's BYOK key for the writer pass | Not used at boot; pasted into UI at call time |

Notes:
- `ANTHROPIC_API_KEY` is intentionally **not** used. Apohara Inti routes
  Claude via OpenRouter so end-users never need an Anthropic key.
- Any unset key short-circuits the matching attacker seat to a fail-open
  verdict (see `packages/backend/main.py:340-353` for the fallback path
  in `_run_attackers`). The verdict aggregator still produces a result
  with whatever subset of the 9 attackers are reachable.

---

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/SuarezPM/apohara-inti.git
cd apohara-inti

# 2. Export the aggregator keys (or use a deploy/.env file)
export OPENROUTER_API_KEY=...
export OPENCODE_ZEN_API_KEY=...
export MINIMAX_API_KEY=...
export NVIDIA_API_KEY=...

# 3. Build and start the 4-service stack
cd deploy
docker-compose up -d --build

# 4. Verify the stack is alive
docker-compose ps               # all 4 services should be Up / healthy
curl -sf http://localhost:8080/health   # proxies through to aegis-backend
```

The stack exposes a single user-facing port (8080 on the Lobster Trap proxy).
The other services bind only inside the `apohara-inti` docker network.

---

## Smoke test

```bash
cd deploy
docker-compose up -d --build
sleep 30                          # give services time to start + healthcheck
curl -sf http://localhost:8080/health
```

Expected response (proxied transparently by Lobster Trap from the backend):

```json
{"status":"ok","deps":{"aegis":"loaded","contextforge":"loaded"},"version":"0.1.0"}
```

If the upstream `apohara-aegis` or `apohara-context-forge` install fails
inside `aegis-backend` (e.g., transient git fetch failure), the response
is HTTP 503 with `{"status":"degraded","deps":{"aegis":"error: ...",...}}`
— still proxied verbatim by Lobster Trap.

**Note on the AC#4 expected shape.** The original sprint AC#4 sketched a
hand-aggregated response `{"lt": "active", "aegis": "active", "inv15":
"enforced"}`. The real Lobster Trap is a transparent reverse proxy that
does not rewrite response bodies (see [`cmd/serve.go:53-87` upstream][lt-serve]),
so the live response is whatever the backend returns — not a synthesized
shape. We chose to honor the proxy's transparency rather than wrap the
backend in a custom aggregator: it is the honest representation of how
the integration behaves in production. See `AUDIT.md` entry #5 for the
full deviation note.

To verify the Lobster Trap is the one serving the request rather than
the backend directly, hit the proxy's built-in dashboard:

```bash
curl -sI http://localhost:8080/_lobstertrap/    # 200 OK, served by LT itself
```

To verify the VeeaONE stub is reachable from inside the network:

```bash
docker exec apohara-inti-backend \
    curl -sf http://veeaone-stub:9000/healthz
# {"status":"ok","vendor":"veea-stub","control_plane":"terrafabric-mock"}
```

---

## VeeaONE stub — what it is and what it isn't

The `veeaone-stub` service is a **20-line FastAPI mock** at
`deploy/veeaone_stub/mock_server.py` that returns canned JSON for three
endpoints (`/healthz`, `/devices`, `/policies`). It exists so that
integration tests can verify the docker network wiring without hitting
Veea's production TerraFabric API.

> **This is a mock VeeaONE control plane for local development.**
> **Production deployments would connect to the real TerraFabric control**
> **plane via Veea's API** ([Veea TerraFabric announcement, MWC 2026][tf-mwc]).

The stub does NOT implement device discovery, policy push, telemetry sync,
or any of the actual control-plane responsibilities TerraFabric provides.
A production swap-in would replace the `veeaone-stub` service with a
Veea-issued client that authenticates against the real TerraFabric API
and pushes policies into the Lobster Trap proxy.

---

## Image registry

For now the recipe **builds all four images locally** via `docker-compose
up -d --build`. The build context is the repo root (one level up from this
directory) so the backend Dockerfile can `COPY packages/backend/...`.

Publishing the built images to `ghcr.io/suarezpm/apohara-inti-*` is
deferred to US-010 (deployment). Expect tags like:

- `ghcr.io/suarezpm/apohara-inti-backend:0.1.0`
- `ghcr.io/suarezpm/apohara-inti-contextforge:0.1.0`
- `ghcr.io/suarezpm/apohara-inti-lobstertrap:0.1.0`
- `ghcr.io/suarezpm/apohara-inti-veeaone-stub:0.1.0`

---

## Reference links

- **Lobster Trap (Veea source)** — <https://github.com/veeainc/lobstertrap>
  (Go 1.22+, transparent DPI reverse proxy, default :8080, no Docker Hub
  image as of 2026-05-16 → we build from source in `Dockerfile.lobstertrap`)
- **Veea TerraFabric (MWC 2026 announcement)** — [aithority.com][tf-mwc]
- **Apohara Inti backend** — `packages/backend/main.py` (FastAPI service,
  `/v1/verify` endpoint, 11 passing tests per AUDIT entry #3)
- **Apohara Context Forge** — <https://github.com/SuarezPM/Apohara_Context_Forge>
  (`apohara_context_forge.mcp.server`, INV-15 enforcement)

[tf-mwc]: https://aithority.com/machine-learning/veea-launches-terrafabric-paving-the-way-to-operate-ai-and-autonomous-systems-at-the-edge/
[lt-serve]: https://github.com/veeainc/lobstertrap/blob/main/cmd/serve.go

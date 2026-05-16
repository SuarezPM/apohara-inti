# Apohara Inti — Deployment

Live URL (TechEx 2026 judging window): <https://149.28.56.91.nip.io/>

This directory holds the production deployment recipe for the Inti
backend (Vultr cloud-compute + Caddy auto-TLS + uvicorn) and the
optional Vercel frontend config.

## Files

| File | Purpose |
|---|---|
| `cloud-init.yaml` | Ubuntu 24.04 bootstrap script run on first boot. Installs Caddy + Python venv + clones aegis/contextforge sibling repos, writes the 0600 `.env`, brings up `apohara-inti.service`, locks UFW to 22/80/443. |
| `vultr_provision.py` | Idempotent provisioner. Substitutes vendor keys + SSH pubkey into `cloud-init.yaml` (in memory; never written to disk), base64-encodes, and POSTs to the Vultr v2 API. |
| `smoke_test.py` | 4-probe end-to-end test (frontend root, `/health`, `/v1/verify`, `/v1/audit/{id}`). Writes timestamped JSON to `../logs/`. |
| `README.md` | This file. |

> Note: this directory also contains `Dockerfile.*` + `docker-compose.yml`
> + `terrafabric-stack.md` + `veeaone_stub/` from US-009 (TerraFabric +
> LobsterTrap docker-compose recipe). Those are a separate deployment
> path and are not used by `vultr_provision.py`.

## Quickstart — provision a new droplet

```bash
# 1. Load vendor keys from your environment.d file.
source ~/.config/environment.d/98-apohara-aegis-keys.conf

# 2. Hard-required: SSH pubkey (cloud-init disables root + password auth).
export INTI_SSH_PUBKEY="$(cat ~/.ssh/id_ed25519.pub)"

# 3. Vultr API key (already in 98-apohara-aegis-keys.conf as VULTR_API_KEY).

# 4. Provision (or get existing IP if a tagged instance exists).
python3 deploy/vultr_provision.py

# Expected output:
#   id     : <uuid>
#   ip     : <new ip>
#   ssh    : ssh inti@<ip>
#   url    : https://<ip>.nip.io/
#   health : https://<ip>.nip.io/health
```

Cloud-init takes ~4-7 min from provision to live URL. Tail
`/var/log/apohara-inti-bootstrap.log` over SSH if the public probe
takes longer.

## SSH access

The Vultr droplet disables root + password auth. SSH as the `inti`
sudoer with the pubkey that was set at provision time. **Note:**
some routes apply an IP_TOS that Vultr's network filter drops on
fresh boxes; if `ssh` times out where `nc -z` succeeds, pass
`-o IPQoS=none`:

```bash
ssh -o IPQoS=none inti@149.28.56.91
```

## Smoke test

```bash
source ~/.config/environment.d/98-apohara-aegis-keys.conf
FRONTEND_URL=https://149.28.56.91.nip.io \
  BACKEND_URL=https://149.28.56.91.nip.io \
  INTI_TEST_GEMINI_KEY="$GEMINI_API_KEY" \
  python3 deploy/smoke_test.py
```

Writes `logs/deploy_smoke_<unix_ts>.json` with the 4 probe outcomes
and exits 0 if `/health` returned 200.

## Tear down

```bash
export VULTR_API_KEY='...'
python3 deploy/vultr_provision.py --destroy
```

Destroys the instance tagged `apohara-inti-techex2026-demo`. The
operator is responsible for confirming the box is the right one
before running this.

## Cost

* Plan: `vc2-1c-2gb` (1 vCPU / 2 GB / 50 GB SSD)
* Region: `ewr` (Piscataway, NJ)
* Hourly rate: \$0.014/hr = \$0.336/day = ~\$10/month if left running
* TechEx 2026 sprint window cost (May 14 – May 26): ~\$4.40

## Vercel frontend deploy (manual — requires OAuth)

The static React bundle in `packages/frontend/dist/` is currently
served by Caddy on the Vultr droplet (same origin as the backend, no
CORS preflight needed). If you want the prettier
`apohara-inti.vercel.app` subdomain instead:

```bash
cd packages/frontend
npx --yes vercel login         # opens browser for device-code OAuth
npx --yes vercel link          # links this dir to a Vercel project
npx --yes vercel deploy --prod # picks up vercel.json + .env.production
```

After deploy, both the Vercel URL and the Vultr nip.io URL will
work. The Vercel one is for the README/blog; the Vultr one stays
live as the canonical backend endpoint that the bundle calls.

## Backend journal

```bash
ssh -o IPQoS=none inti@149.28.56.91 sudo journalctl -u apohara-inti -n 100 --no-pager
ssh -o IPQoS=none inti@149.28.56.91 sudo journalctl -u caddy        -n 100 --no-pager
```

## Caddyfile

The Caddyfile is generated at boot (or by `deploy/cloud-init.yaml`
step 5). To inspect or modify the live config:

```bash
ssh -o IPQoS=none inti@149.28.56.91 sudo cat /etc/caddy/Caddyfile
```

Current layout: route `/health`, `/v1/*`, `/docs`, `/openapi.json`,
`/redoc` to uvicorn on 127.0.0.1:8000; everything else served as the
static SPA bundle from `/opt/apohara-inti-static/`.

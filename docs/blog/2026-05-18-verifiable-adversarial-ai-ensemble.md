---
title: "How to build a verifiable adversarial AI ensemble"
date: 2026-05-18
author: Pablo M. Suarez
tags: [ai-security, adversarial-validation, llm-evaluation, formal-methods, hackathon]
canonical_url: https://www.apohara.dev/blog/2026/05/18/verifiable-adversarial-ai-ensemble
license: CC-BY-4.0
---

# How to build a verifiable adversarial AI ensemble — Apohara PROBANT's hackathon sprint

---

## 1. The problem with single-vendor AI code review

Every AI coding assistant on the market today runs review loops that look
roughly like: send code to one provider, get feedback, send feedback back to
the same provider, iterate. Cursor's review mode, GitHub Copilot's explain
feature, Gemini Code Assist — all of them ask one vendor to both write and
review. That is best-of-N sampling from the same distribution, not adversarial
validation.

The problem is subtle but consequential. Large language models from a single
vendor share a training distribution. They share the same pretraining corpus
biases, the same RLHF policy quirks, the same systematic blind spots. A
Claude model reviewing Claude output will miss the same categories of
vulnerabilities that Claude tends to produce. A GPT-4-class model reviewing
GPT-4 code has the same property. This is not a bug in any single model — it
is a structural property of using one provider's distribution to check its own
outputs.

The 2026 OWASP Top 10 for LLM Applications elevated Tool Poisoning (LLM02)
near the top of the list precisely because the attack surface has expanded as
coding agents acquire the ability to read files, run shell commands, and push
to version control. Prompt injection embedded in a dependency's docstring,
a README fetched from an untrusted repo, or a code comment in a third-party
package can all influence a coding agent's next action. Almost none of the
tools in widespread use today have a structural answer to this threat — they
rely on the same vendor's safety filters, which an adversary who understands
the model's behavior can probe and eventually evade.

We competed in two hackathons in seven days — TechEx 2026 (Intelligent
Enterprise Solutions, May 14–26) and Milan AI Week 2026 (AI Agent Olympics,
deadline May 20). Looking at the six other teams in our competitive group,
the pattern was identical across all of them: polished landing pages, claimed
accuracy numbers in the 98–99.9% range with no attached measurement logs, and
a single Gemini 2.5 Flash backend handling both writing and reviewing. Not one
competitor published a test suite, a measurement JSON, or a paper.

That gap is what Apohara PROBANT was built to fill.

---

## 2. 9-vendor adversarial design with INV-15 isolation

The core insight is simple: if you want adversarial validation, use
adversaries from different vendors. An ensemble of nine frontier LLMs from
nine different organizations cannot share training-distribution blind spots
the way a single vendor's models can. When a majority of nine independently
trained models flag the same pattern as harmful, that is a signal worth
acting on. When only one or two flag it, the operator can route it to human
review rather than an automatic block.

PROBANT's ensemble runs through OpenRouter and includes:
Claude Opus 4.7, GPT-5.5, DeepSeek V4 Pro, MiniMax M2.7, Kimi K2.6,
GLM 5.1, Qwen 3.6 Plus, Nemotron 3 Super 120B, and Big Pickle. These
represent North American, Chinese, and European model families — three
distinct regulatory environments and at minimum three distinct pretraining
corpora.

Verdict aggregation is a transparent rule defined in `main.py`:

```python
# packages/backend/main.py

# Verdict aggregation thresholds (per acceptance criteria 1.f).
VERDICT_BLOCK_THRESHOLD = 6   # >=6 attackers harmful  -> blocked
VERDICT_REVIEW_THRESHOLD = 3  # 3-5 attackers harmful  -> risky
# (else verified)

def _aggregate_verdict(reports: list[AttackerReport]) -> str:
    """Map attacker harmful-count to verdict string per acceptance criteria."""
    harmful_count = sum(1 for r in reports if r.found_issue)
    if harmful_count >= VERDICT_BLOCK_THRESHOLD:
        return "blocked"
    if harmful_count >= VERDICT_REVIEW_THRESHOLD:
        return "risky"
    return "verified"
```

0–2 attackers finding an issue → **verified**. 3–5 → **risky** (routes to
human review). 6 or more → **blocked**. The thresholds are in the source
code, not a config file or a model's reasoning — they are auditable and
deterministic.

The nine attacker calls run in parallel with a per-call cost ceiling:

```python
# packages/backend/main.py

async def _run_attackers(
    adapters: list[Any],
    prompt: str,
) -> tuple[list[JudgeVerdict], float, bool]:
    """Run the 9 adversarial adapters in parallel with a cost ceiling.

    Returns (verdicts, cumulative_cost_usd, cost_capped). When the running
    cost exceeds COST_CEILING_USD mid-batch, remaining adapters are
    short-circuited to an out_of_budget verdict (not harmful, not active).
    """
    base_cost = sum(getattr(ad, "cumulative_cost_usd", 0.0) for ad in adapters)

    async def _wrapped(ad: Any) -> JudgeVerdict:
        live_cost = (
            sum(getattr(a, "cumulative_cost_usd", 0.0) for a in adapters)
            - base_cost
        )
        if live_cost >= COST_CEILING_USD:
            return JudgeVerdict(
                is_harmful=False, confidence=0.0,
                reason="per-call cost ceiling reached",
                error=f"cost_capped_per_call_usd={COST_CEILING_USD}",
                path="out_of_budget",
                # ... other fields
            )
        try:
            return await ad.evaluate(prompt)
        except Exception as exc:  # noqa: BLE001
            return JudgeVerdict(
                is_harmful=False, confidence=0.0,
                error=f"transport: {exc!s}"[:160],
                path="unavailable",
                # ... other fields
            )

    verdicts = await asyncio.gather(*(_wrapped(ad) for ad in adapters))
    delta_cost = (
        sum(getattr(ad, "cumulative_cost_usd", 0.0) for ad in adapters)
        - base_cost
    )
    cost_capped = delta_cost >= COST_CEILING_USD
    return list(verdicts), float(delta_cost), bool(cost_capped)
```

Memory isolation between the Gemini writer session and every attacker is
enforced by INV-15 — a formal safety invariant from Apohara ContextForge
(`apohara_context_forge.safety.jcr_gate.JCRSafetyGate`). INV-15 guarantees
that no attacker's KV-cache entry is readable by the writer's context
registry, and vice versa. The invariant is proven in the companion paper
(DOI [10.5281/zenodo.20114594](https://doi.org/10.5281/zenodo.20114594)).
This matters because without isolation, an adversarial attacker could
poison the writer's context via shared cache state — the memory plane
becomes an attack vector.

---

## 3. HMAC verdict chain — tamper-evident audit trail

Every `/v1/verify` response includes three fields alongside the verdict:
a `prev_hash`, a `signed_hash`, and an HMAC-SHA256 `signature`. Together
they form an append-only chain-of-custody ledger stored at
`~/.apohara-inti/ledger.jsonl`. Any judge, auditor, or investor can
re-derive both independently and detect any of three classes of tampering:
payload mutation, signature mutation, or key rotation.

The implementation is a Python port of Apohara Guard's TypeScript
`EvidenceVault` (`src/evidence/{vault,chain,crypto}.ts`):

```python
# packages/backend/verdict_vault.py

def append(self, entry: dict[str, Any]) -> dict[str, str]:
    """Append entry with prev_hash + signed_hash + signature.

    Returns the three derived fields so callers can echo them.
    """
    self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
    prev_hash = self.read_last_hash()
    payload = dict(entry)
    payload["prev_hash"] = prev_hash
    canonical = self._canonical(payload)
    signed_hash = hashlib.sha256(
        (prev_hash + canonical).encode("utf-8")
    ).hexdigest()
    payload["signed_hash"] = signed_hash
    signature = self._sign(canonical + signed_hash)
    payload["signature"] = signature
    with self.ledger_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, sort_keys=True) + "\n")
    return {
        "prev_hash": prev_hash,
        "signed_hash": signed_hash,
        "signature": signature,
    }
```

`verify_chain()` walks the entire ledger and re-derives each entry:

```python
# packages/backend/verdict_vault.py

def verify_chain(self) -> tuple[bool, list[str]]:
    """Walk the ledger, re-derive each signed_hash + signature.

    Returns (is_valid, errors). errors is empty on success.
    Detects: malformed JSON, missing fields, prev_hash mismatch,
    signed_hash mismatch (payload tampered), signature mismatch
    (HMAC tampered or key rotated).
    """
    errors: list[str] = []
    # ...
    prev_hash = ZERO_HASH
    for line_no, line in enumerate(fh, 1):
        entry = json.loads(line)
        claimed_hash = entry.get("signed_hash")
        claimed_sig = entry.get("signature")
        # Re-derive signed_hash from canonical payload (strip derived fields).
        redo = dict(entry)
        redo.pop("signed_hash", None)
        redo.pop("signature", None)
        canonical = self._canonical(redo)
        expected_hash = hashlib.sha256(
            (prev_hash + canonical).encode("utf-8")
        ).hexdigest()
        if expected_hash != claimed_hash:
            errors.append(
                f"line {line_no}: signed_hash mismatch "
                f"(payload tampered; expected {expected_hash}, "
                f"got {claimed_hash})"
            )
        expected_sig = self._sign(canonical + claimed_hash)
        if not hmac.compare_digest(expected_sig, claimed_sig):
            errors.append(
                f"line {line_no}: signature mismatch "
                f"(HMAC tampered or key rotated)"
            )
        prev_hash = claimed_hash
    return len(errors) == 0, errors
```

The HMAC key is loaded from the `APOHARA_LEDGER_HMAC_KEY` environment variable.
If the variable is not set, the vault issues a `RuntimeWarning` and falls back
to an ephemeral per-process key — signatures survive the current run but not
restarts. Production deployments must set the env var; this behavior is
documented in the README and enforced by a check in `/health`.

One design decision worth noting: the `verify_chain()` call is not in the
hot path of `/v1/verify`. It is exposed via `GET /v1/audit/{verdict_id}` and
runs on-demand. The audit endpoint fetches a single entry by `signed_hash` and
returns it with its signature for spot-checking. Full chain verification is a
maintenance operation, not a per-request operation.

---

## 4. Measurement methodology — Wilson 95% CI, n=80 holdout, honesty discipline

The two hardest things to resist in a hackathon are the temptation to claim
round numbers and the temptation to omit caveats. Both will destroy credibility
with technically literate judges faster than having a lower real number.

Here are the actual measurements.

**JailbreakBench (JBB-Behaviors) ensemble block rate:**
93.75% (Wilson 95% CI [86.2%, 97.3%], n=80 holdout).
Source: `logs/baseline_aegis-ensemble-10frontier_day5_FALLBACK_20260515T212737Z.json`
in the [apohara-aegis repo](https://github.com/SuarezPM/apohara-aegis).

**LobsterTrap DPI pre-check, as of 2026-05-18T15:54Z:**

| Bucket | n | Block rate | Wilson 95% CI | CI width | Note |
|---|---|---|---|---|---|
| SQL injection | 20 | 50% | [29.9%, 70.1%] | 0.40 | directional, n too small to publish as headline |
| Prompt injection | 10 | 30% | [10.8%, 60.3%] | 0.50 | directional, n too small to publish as headline |
| Benign (FP rate) | 51 | 9.8% FP | [4.3%, 21.0%] | 0.17 | usable |

Source: `logs/lobstertrap_block_rate_20260518T155431Z.json` in this repo.

The caveats are baked into the log file itself:

```json
{
  "methodology": {
    "caveats": [
      "sqli: small-sample n=20, directional only",
      "prompt_injection: small-sample n=10, directional only"
    ]
  },
  "buckets": {
    "sqli": {
      "n": 20,
      "blocks": 10,
      "block_rate": 0.5,
      "wilson_95_ci": [0.2993, 0.7007],
      "ci_width": 0.4014
    },
    "benign_false_positive": {
      "n": 51,
      "blocks": 5,
      "fp_rate": 0.098,
      "wilson_95_ci": [0.0426, 0.2098]
    }
  }
}
```

The CI width rule we use: if the Wilson CI width exceeds 0.30, the number
is directional only — it tells you which way the system is pointing but
not how far. We use it internally for iteration. We do not report it
as a headline number. The JBB block rate at n=80 has CI width 0.11, which
is narrow enough to publish. The LobsterTrap SQLi number at n=20 has CI
width 0.40 — useful for tuning the DPI ruleset, not for marketing.

Competitors submitted claims like "98% accuracy" and "99.9% uptime"
with no attached evidence. One competitor's README had a hardcoded
`duration_ms = 0.82` in its benchmark section. We found this while
reading source code because we always read the source code of our
competitive set. The numbers were not from measurements; they were typed.

This is not a uniquely hackathon problem. Production AI safety tools
routinely publish accuracy numbers derived from cherry-picked evaluation
sets with no CI, no holdout discipline, and no public log files. The
honesty discipline in Apohara PROBANT is drawn from the AUDIT.md culture
in Apohara ContextForge, where every overclaim from V6.0 was publicly
documented with file:line evidence and tracked through closure. Ten items
closed in V7.0.0-rc.2.

---

## 5. Lessons learned from a 7-day hackathon sprint

**Parallel execution beats sequential.** The biggest speedup in the sprint
came from running independent subtasks simultaneously: frontend redesign,
backend endpoint wiring, measurement runs, and submission drafting all
advanced in parallel rather than in sequence. A pipeline of specialized
agents (writer → security reviewer → measurement runner → submission editor)
cut the wall-clock time on each story by roughly half compared to sequential
execution. The bottleneck was always the human review checkpoint, not the
implementation.

**A 50% measured block rate is more credible than a 95% claimed one.**
When we presented the LobsterTrap SQLi result to the submission reviewers
as "50% block rate (n=20, directional, Wilson CI [29.9%, 70.1%])", we got
more engagement than we would have from a bolder uncited claim. The CI
and the caveat signal that the number came from an actual measurement
process. Judges who evaluate multiple submissions develop a fast heuristic
for "did this team measure this or type this?" — and the heuristic is
usually right.

**Brand vs. substance.** Six of the seven teams in our competitive group
had landing pages more polished than ours at the midpoint of the sprint.
None of them had a test suite, a paper, or a measurement log. By the
submission deadline, the substance gap had widened: we had 350+ pytest
tests, 15+ measurement JSON files, a peer-reviewable paper with a Zenodo
DOI, and multi-hardware validation on AMD MI300X and NVIDIA H100. Two of
the six teams had a README. This is not a comment on their engineering
ability — it is a comment on what a 7-day sprint optimizes for when you
have not decided in advance what "done" means.

**Production fragility is real and SSH breaks.** The Vultr droplet SSH
access broke twice in seven days — once due to a key rotation error and
once due to a network reconfiguration. Both times we had a recovery path
because we had built one: Docker Compose with a restart policy, a Caddy
reverse proxy with automatic TLS, and a health endpoint (`GET /health`)
that the CI smoke tests against. Every breaking change went through the
smoke test before we declared it deployed. The habit of building rollback
paths before you need them is the difference between a 45-minute outage
and a 4-hour one.

**Architecture lock-in is a decision, not an accident.** We chose to run
LobsterTrap in subprocess mode (invoking the `lobstertrap inspect` CLI
directly) rather than in reverse-proxy mode (routing all traffic through
LobsterTrap's HTTP interface). The reason was that subprocess mode
preserves the Gemini SDK's connection lifecycle and avoids adding a
synchronous HTTP hop in the critical path of `/v1/verify`. The cost is
that subprocess mode is slower to refactor away from if LobsterTrap
changes its CLI interface. We documented this decision in
`packages/backend/lobstertrap_client.py` with a comment explaining the
trade-off. Undocumented architecture decisions compound into technical
debt faster than any other kind.

---

The live demo is at **[https://149.28.56.91.nip.io/](https://149.28.56.91.nip.io/)** (TechEx judging window, no signup required). The source code is at [github.com/SuarezPM/apohara-inti](https://github.com/SuarezPM/apohara-inti) (Apache-2.0). The ContextForge paper and formal INV-15 proof are at DOI [10.5281/zenodo.20114594](https://doi.org/10.5281/zenodo.20114594).

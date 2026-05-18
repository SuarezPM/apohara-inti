# Judge FAQ — Apohara PROBANT (TechEx 2026)

> Defensive Q&A for judges reviewing the submission. Every answer cites a
> verifiable artifact: a log file, a file:line reference, a commit SHA, or a
> runnable command. If something is not yet done, it says so.

---

## Introduction

Apohara PROBANT is a cross-AI code verification platform. A user submits code
or a code-review request; Gemini writes an initial review (BYOK); a 12-vendor
adversarial ensemble independently audits that review for prompt injection,
vulnerabilities, and logic bugs; every verdict is HMAC-signed into a tamper-
evident ledger. The core safety invariant — INV-15, KV-cache isolation between
judge agents — is proven by a Z3 SMT solver and validated empirically across
1,210 random calls (0 violations). This document answers the ten questions most
likely to arise during a technical review.

---

## Q1: What does running 12 vendors actually cost in production?

The per-vendor spend cap is **$5.00 USD per vendor per ensemble lifetime**,
defined in `apohara-aegis/apohara_aegis/multi_judge.py:1537` as
`DEFAULT_COST_CAPS_USD`. The Phase-3 expansion (2026-05-18) raised the
cumulative ceiling from $45 to **$60** when three new seats were added at $5
each; the CHANGELOG entry reads: "raising the cumulative paid envelope from
$45 → $60 per ensemble lifetime" (`apohara-aegis/CHANGELOG.md`, "Unreleased"
section, "Changed" subsection).

For the Day-5 fallback run (`logs/baseline_aegis-ensemble-10frontier_day5_FALLBACK_20260515T212737Z.json`),
`cost_est_usd` was effectively $0 because that particular run used cached
adapter stubs for cost accounting. The per-vendor rates come from the adapter
class definitions in `multi_judge.py` (fields `cost_per_input_tok`,
`cost_per_output_tok`). The HarmBench n=40 benchmark
(`apohara-aegis/logs/harmbench_subset40_20260516T130529Z.json`) shows a real
measured run cost of **$0.67 USD** for 40 prompts × 10 active vendors — that
is approximately $0.017 per prompt for the full adversarial ensemble.

**Honest limitation on vendor count.** Two of the twelve adapter classes —
`OpenRouterGrok2Adapter` (model ID `x-ai/grok-2-1212`) and
`OpenRouterPerplexitySonarLargeAdapter` (model ID
`perplexity/llama-3.1-sonar-large-128k-online`) — were verified not present in
the OpenRouter catalogue as of 2026-05-18. Both adapters ship in the codebase
and fail open (returning `path='unavailable'`) per the base-class contract
documented in `multi_judge.py:110`. The live production ensemble is therefore
**10 working vendors + 2 staged adapters**, not 12 live simultaneously. The
CHANGELOG entry for the Phase-3 expansion states this explicitly under
"KNOWN-LIMITATION" notes for each affected adapter class.

---

## Q2: INV-15 vs runtime guarantee — what does the Z3 SMT proof actually prove?

**What is proven.** The Z3 SMT solver proves that the *negation* of INV-15 is
unsatisfiable (`unsat`) under the propositional model encoded in
`apohara_context_forge/safety/z3_inv15_proof.py`. The proof runs in
**10.08 ± 0.5 ms** (mean over 10 trials on AMD MI300X) as reported in the
paper (`Apohara_Context_Forge/paper/inv15_paper.pdf`, v3.0, section "Formal
Verification via Z3 SMT", line ~1124 of the LaTeX source). Z3 returns `unsat`
when asked whether any real-valued assignment of `agent_role_critic`,
`candidate_count`, `reuse_rate`, `layout_shuffled`, `risk_score`, and
`use_dense_prefill` can simultaneously satisfy INV-15's antecedent and violate
its consequent. Commit `4a3f73c` in Apohara_Context_Forge adds both the proof
code and the paper v3.0 section. Commit `35be412` in the same repo lands the
`z3_inv15_proof.py` module.

**What is not proven.** The SMT proof operates on an abstract model that
mirrors the constants and decision logic in `jcr_gate.py`. It does not prove
that the implementation correctly instantiates the abstract model under all
possible runtime conditions (out-of-memory, preemption, race conditions in the
KV-cache eviction path, etc.). The empirical complement — 0 violations across
1,210 sampled calls, logged in `Apohara_Context_Forge/logs/` — validates
implementation behavior at the same constants the Z3 model encodes. The paper
is explicit about this scope boundary (DOI 10.5281/zenodo.20114594). The two
layers triangulate from formal model to running code; neither alone is
sufficient.

---

## Q3: LobsterTrap pre-check — what's the threat model? What does it actually block?

LobsterTrap (by Veea Inc., MIT-licensed, independent of Apohara) is invoked as
a subprocess DPI pre-check on every `/v1/verify` request. The client code is
`packages/backend/lobstertrap_client.py`; the policy template is
`configs/lobstertrap-policy.example.yaml`. LobsterTrap inspects the raw prompt
before it reaches Gemini or the adversarial ensemble.

**Measured block rates** from
`logs/lobstertrap_block_rate_20260518T155431Z.json` (run 2026-05-18T15:54:31Z):

| Bucket | n | Block rate | Wilson 95% CI |
|---|---|---|---|
| SQL injection | 20 | 50.0% | [29.9%, 70.1%] |
| Prompt injection | 10 | 30.0% | [10.8%, 60.3%] |
| Benign (false positive) | 51 | 9.8% FP | [4.3%, 21.0%] |

The CI half-widths are wide because the sample sizes are small (n=20 and n=10
for the adversarial buckets). These numbers are directional, not definitive.

**Honest gap.** LobsterTrap's policy uses `contains_injection_patterns` +
`intent_category=data_access` + risk-score thresholds. SQL injection variants
that omit a `SELECT` keyword — for example, `admin OR 1=1` — receive
`intent_category=general` and are **not blocked at the LobsterTrap layer**.
These reach the 9-vendor adversarial ensemble as the next defensive layer.
This gap is disclosed in `SECURITY.md` under "Honest disclosures." LobsterTrap
is the first of a four-layer defense chain; it is not claimed to be exhaustive.

---

## Q4: HarmBench 77.5% block rate — how do you interpret the wide Wilson CI?

The HarmBench measurement is in
`apohara-aegis/logs/harmbench_subset40_20260516T130529Z.json` (run
2026-05-16T13:26:30Z). Summary:

- **n = 40 prompts** from `harmbench-text-test-subset40-seed42`
- **total_blocked = 31** → overall_block_rate = **0.775**
- **Wilson 95% CI: [62.5%, 87.7%]** (halfwidth ±12.6%)

The wide CI is a direct consequence of n=40. A Wilson interval on 31/40 has
a half-width of ±12.6 percentage points; at n=400 it would shrink to roughly
±4 pp. The reason we ran n=40 rather than n=400 is budget: the run cost was
**$0.67 USD** against a ceiling of `cost_ceiling_usd = 40.0` (field in the
log). At $0.67/40 = ~$0.017/prompt, n=400 would cost roughly $6.70 — within
budget — but was not prioritized during the hackathon sprint. The CI is wide
and we report it as such.

**Per-category breakdown** (from the log's `records` field, 40 total):

| Category | Blocked | Total | Rate |
|---|---|---|---|
| illegal | 10 | 10 | 100% |
| chemical_biological | 6 | 6 | 100% |
| misinformation_disinformation | 5 | 5 | 100% |
| harassment_bullying | 4 | 4 | 100% |
| cybercrime_intrusion | 4 | 4 | 100% |
| harmful | 2 | 3 | 67% |
| copyright | 0 | 8 | 0% |

Copyright is 0/8 by design: copyright infringement detection is outside the
threat model for an adversarial code-verification tool. Excluding copyright,
**31/32 = 96.9%** on harm-vector rows. The `honesty_note` field in the log
confirms: "HarmBench subset N=40 seed=42 measured 2026-05-16; complements
JBB-Behaviors n=80 (93.75% +/- 2.7%) baseline."

---

## Q5: Apache-2.0 vs AGPL-3.0 across the trinity — why the split?

The project spans three repositories with deliberate license choices:

- **Apohara PROBANT** (this repo, formerly apohara-inti): **Apache-2.0**
  (`LICENSE` at repo root). Enterprise procurement for safety tooling is
  harder with copyleft. Apache-2.0 allows commercial use without source-
  disclosure obligations.
- **Apohara Context Forge** (`SuarezPM/Apohara_Context_Forge`): **Apache-2.0**
  (`Apohara_Context_Forge/LICENSE`). Same rationale — the INV-15 invariant and
  codec are intended as infrastructure that enterprises can embed.
- **Apohara Guard** (sister project, separate repo): **AGPL-3.0**. Guard
  handles Trust & Safety / CSAM detection. Copyleft on detection-pattern
  improvements preserves community ownership: any organization deploying Guard
  must contribute improvements back to the commons. This is intentional and
  disclosed in `SECURITY.md` under "Honest disclosures": "The sister-project
  Apohara Guard (AGPL-3.0, separate repo) handles Trust & Safety / CSAM
  detection."

To verify: `grep -r "AGPL\|Apache" apohara-inti/LICENSE apohara-context-forge/LICENSE`.

---

## Q6: MI300X vs H100 reproducibility — what hardware was actually used?

Two distinct hardware environments were used and logged:

**AMD Instinct MI300X** — 192 GB HBM3, ROCm 7.2.0. Accessed via Hot Aisle
AMD AI Dev Cloud at $1.99/h. The hardware label used in all honest logging is
`"rocm-hip:6.2.41133:AMD Instinct MI300X VF"` — NOT `"cuda"`, even though
PyTorch ROCm reuses the `torch.cuda.*` API for backward-compatibility. The
`scripts/check_honesty.sh` CI guard catches label drift. MI300X measurement
logs are in `Apohara_Context_Forge/logs/`: `mi300x_extreme_scale_*.json`,
`mi300x_hbm3_bandwidth_*.json`, `mi300x_fwht_*.json`, `mi300x_lmcache_*.json`
(multiple runs across Wave B and Wave C). The AUDIT.md entries §16–§17 in
Apohara_Context_Forge document which measurements are real MI300X runs vs.
CPU fallbacks with explicit labeling.

**NVIDIA H100** — accessed via Vultr droplet. The 5-agent benchmark in
`Apohara_Context_Forge` (commit `ff5e187`: "real H100 5-agent measurement
(US-014 close) replaces CPU-mock") landed real H100 numbers after replacing a
CPU mock. Log: `Apohara_Context_Forge/logs/` directory.

Both sets of logs are committed to the respective repos. The Zenodo DOI
10.5281/zenodo.20114594 covers the v2.0.1 paper with the MI300X sweep (0/1210
INV-15 violations). The v3.0 paper (commit `4a3f73c`) adds the Z3 formal proof
layer.

**Verification command:**
```bash
grep '"hardware"' Apohara_Context_Forge/logs/mi300x_extreme_scale_*.json
```

---

## Q7: Single-developer claim — really one person? How do we verify?

Run the following across all three repos:

```bash
git -C apohara-inti log --format='%an %ae' | sort -u
git -C Apohara_Context_Forge log --format='%an %ae' | sort -u
git -C apohara-aegis log --format='%an %ae' | sort -u
```

All three return: `Pablo p.ms.08@hotmail.com` (and a GitHub no-reply alias
`110942776+SuarezPM@users.noreply.github.com` for web-editor commits).
Pablo M. Suarez, UNT Argentina.

**Honest note on tooling.** AI coding tools (Claude Code / Claude Sonnet 4.6)
were used throughout the hackathon as a productivity multiplier. All design
decisions, architecture choices, test assertions, and honesty discipline
enforcement are Pablo's. AI assistance is not co-authorship; it is closer to
a compiler that generates candidate code. The `git log` trail shows a single
human committer.

---

## Q8: What's NOT shipped — your honest gap list

The following are named in documentation but have limitations, are planned
artifacts, or are explicitly not active:

**Certification vs. planning artifacts.**
`docs/compliance/soc2-control-mapping-2026.md` and
`docs/compliance/iso27001-control-mapping-2026.md` exist and map controls.
Apohara PROBANT is **NOT SOC2 or ISO 27001 certified**. Certification requires
a 6–12 month organizational engagement with an accredited auditor. Disclosed
in `SECURITY.md`: "SOC 2 / ISO 27001 control mappings exist as planning
artifacts (see docs/compliance/); we are NOT certified."

**Apohara Guard — 5-layer kernel sandbox.**
The claim is "5-layer sandbox." The honest state is **3 layers active + 2
layers planned**: seccomp and pid namespace are live; Landlock LSM and the
full seccomp-bpf blob generation require a `libseccomp` compilation step
scheduled for Phase 3. Disclosed in `SECURITY.md`: "Its 5-layer kernel sandbox
claim is currently honest as 3 layers active + 2 layers planned (Landlock LSM
+ seccomp-bpf require libseccomp bpf blob generation, scheduled Phase 3)."

**LobsterTrap coverage gaps.**
SQL injection variants without a `SELECT` keyword (e.g., `admin OR 1=1`) fall
through the LobsterTrap policy with `intent_category=general` and reach the
adversarial ensemble layer. Not a silent gap — disclosed in `SECURITY.md`.

**12-vendor ensemble live count.**
Two of the twelve adapter classes (Grok-2 and Perplexity Sonar) are staged:
they instantiate and fail open because the model IDs are not in the OpenRouter
catalogue as of 2026-05-18. Live count: **10 working + 2 staged**.

**Threshold rescaling 3/6 → 4/8.**
The verdict aggregation thresholds in `packages/backend/main.py`
(`VERDICT_REVIEW_THRESHOLD = 3`, `VERDICT_BLOCK_THRESHOLD = 6`) are calibrated
for a 9-vendor ensemble. The design doc specifies rescaling to 4/8 for the
12-vendor ensemble. This change has not shipped yet. See Q10.

**`cost_est_usd = 0.0` in Day-5 fallback log.**
The Day-5 fallback log
(`apohara-aegis/logs/baseline_aegis-ensemble-10frontier_day5_FALLBACK_20260515T212737Z.json`)
shows `cost_est_usd = 0.0`. This is because the adapters in that run had
`cost_per_input_tok = 0.0` (stub rate accounting, not mock behavior). Real per-
prompt costs are measured in the HarmBench run: $0.67 for 40 prompts.

---

## Q9: How does this compare to existing AI gateways (LiteLLM, OpenRouter native)?

LiteLLM and OpenRouter are **routing layers**: send a request to one vendor,
get one response back. They solve vendor-agnostic access and load-balancing.

Apohara PROBANT is a **verification layer**: one vendor (Gemini) writes a
response, then a separate adversarial ensemble adjudicates whether that
response is safe, injects a verdict into a HMAC-signed ledger, and the client
gets a signed verdict chain — not just a response. The roles are:

| Concern | LiteLLM / OpenRouter | Apohara PROBANT |
|---|---|---|
| Multi-vendor routing | Yes | Yes (secondary, via aegis) |
| Adversarial verification | No | Yes (10-vendor ensemble) |
| Tamper-evident audit trail | No | Yes (HMAC-SHA256 chain) |
| Formal safety invariant | No | Yes (INV-15, Z3-proven) |
| Prompt envelope protection | No | Yes (Hines et al. 2403.14720) |

These tools are complementary. An enterprise could sit Apohara PROBANT behind
LiteLLM for routing and use PROBANT's `/v1/verify` endpoint for the
verification pass. The design rationale is in
`docs/research/12-vendor-ensemble-design.md` (the "Threat Model" section
explains why single-vendor routing is insufficient for adversarial verification).

---

## Q10: Threshold rescaling 3/6 → 4/8 for 12-vendor — why didn't you ship it?

The current verdict aggregation thresholds in
`packages/backend/main.py` are:
- `VERDICT_REVIEW_THRESHOLD = 3` (≥3 vendors flag harmful → human review)
- `VERDICT_BLOCK_THRESHOLD = 6` (≥6 vendors flag harmful → blocked)

These were calibrated for a 9-vendor ensemble. The
`docs/research/12-vendor-ensemble-design.md` design doc (section "Verdict
Aggregation Threshold Rescaling", approx. line 88) states explicitly:

> "This change must land as a separate PR from the adapter expansion, after
> running the full regression suite with the updated thresholds."

The cascade is larger than it appears. Changing the two threshold constants
touches:
- `test_verify.py:138,157` — tests that assert specific block/review thresholds
- `test_verify_stream.py:190` — streaming test with threshold-dependent assertion
- At least 8 documentation locations referencing the "≥3/≥6" numbers

Shipping this change mid-window during a 5-hour submission deadline creates
test regression risk with no recovery path. The surgical-changes discipline
in `CLAUDE.md §3.3` — "touch only what the task requires" — applies: the
adapter expansion was the scoped task; the threshold rescaling is a dependent
but distinct change that must be validated independently.

The design doc specifies the correct target values (4/8), and the CHANGELOG
entry for the Phase-3 expansion includes a "Recommended (consumer-side, not
enforced here)" note pointing to this rescaling. It is a documented deferred
PR, not a silent overclaim.

---

## Bonus Q: Are you applying to YC?

A YC Summer 2026 application document is prepared at
`docs/strategy/yc-summer-2026-application.md`. Whether the application was
submitted is outside the scope of this hackathon submission.

---

## Bonus Q: What's the pricing model?

The live demo at `https://www.apohara.dev` operates on a BYOK basis for
Gemini (user supplies their own Google AI Studio key via the `gemini_api_key`
POST field) plus a **5 free calls per IP per day** rate-limited tier.
Commercial offering is scoped at `docs/strategy/commercial-offering-2026Q3.md`.
No billing infrastructure is active; the Stripe scaffold in
`packages/backend/billing/stripe_scaffold.py` is a PoC gated behind
`STRIPE_TEST_SECRET` and is not live.

---

## Bonus Q: Production deployment story?

Deployed on a **Vultr droplet** (`149.28.56.91`) with Caddy auto-issued TLS
via Let's Encrypt. A single VM is sufficient for current hackathon load.
Multi-tenant mode (`APOHARA_MULTI_TENANT=1`) is opt-in and default-off; the
single-tenant + BYOK flow is the supported production posture. Caddy reference
is in `README.md:25`. Dependency pins are in
`packages/backend/pyproject.toml`.

---

## Cross-references

| Document | Path |
|---|---|
| Main README | `apohara-inti/README.md` |
| Security policy | `apohara-inti/SECURITY.md` |
| Honesty log (PROBANT) | `apohara-inti/AUDIT.md` (if present; see aegis AUDIT.md) |
| Honesty log (Aegis) | `apohara-aegis/AUDIT.md` |
| Honesty log (Context Forge) | `Apohara_Context_Forge/AUDIT.md` |
| INV-15 paper (PDF) | `Apohara_Context_Forge/paper/inv15_paper.pdf` |
| Zenodo DOI | https://doi.org/10.5281/zenodo.20114594 |
| Phase 3 delta doc | `apohara-inti/docs/submissions/PHASE3-DELTA.md` |
| TechEx 2026 submission | `apohara-inti/docs/submissions/techex-2026-submission.md` |
| Milan AI Week submission | `apohara-inti/docs/submissions/milan-aiweek-2026-submission.md` |
| 12-vendor design doc | `apohara-inti/docs/research/12-vendor-ensemble-design.md` |
| Z3 proof module | `Apohara_Context_Forge/apohara_context_forge/safety/z3_inv15_proof.py` |
| LobsterTrap client | `apohara-inti/packages/backend/lobstertrap_client.py` |
| LobsterTrap policy template | `apohara-inti/configs/lobstertrap-policy.example.yaml` |
| LobsterTrap block-rate log | `apohara-inti/logs/lobstertrap_block_rate_20260518T155431Z.json` |
| HarmBench n=40 log | `apohara-aegis/logs/harmbench_subset40_20260516T130529Z.json` |
| Day-5 JBB ensemble log | `apohara-aegis/logs/baseline_aegis-ensemble-10frontier_day5_FALLBACK_20260515T212737Z.json` |
| Cost cap definition | `apohara-aegis/apohara_aegis/multi_judge.py:1537` |
| Aegis CHANGELOG | `apohara-aegis/CHANGELOG.md` |

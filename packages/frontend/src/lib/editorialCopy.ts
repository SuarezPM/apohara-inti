/** Single-source editorial copy for Apohara Inti frontend.
 *  Pablo reviews this file at Phase 5 AC5.4 (content gate). */

export const HOW_IT_WORKS_COPY = {
  step1: "Paste a PR URL, code diff, or natural-language task. BYOK Gemini key (free tier covers hundreds of runs) or the shared demo key (5 calls per IP per UTC day).",
  step2: "Gemini writes a review. In parallel, 9 frontier vendors adversarially probe both inputs. Each attacker runs in an isolated KV-cache — formal invariant INV-15 enforced by Apohara ContextForge.",
  step3: "Aggregate harmful-count → verdict (verified / risky / blocked). Signed into an append-only SHA-256 ledger chain. Every verdict has a fetchable audit_id pointing at the exact attacker outputs.",
};

export const COMPARISON_HEADER = {
  eyebrow: "Compare honestly",
  title: "Apohara vs the field.",
  narrative:
    "Six other people are building something near this space. Three are peer hackathon entries — we compare directly. Seven are commercial products — we describe the category honestly without grading each per-cell, since one solo dev shouldn't be scoring funded companies on his own webpage. One is IBM Granite Guardian 4, which we measured against directly because the benchmark is public and the comparison is fair.",
};

export const COMPARISON_TIER2_NARRATIVE =
  "Commercial code-review tools — Snyk Code, Semgrep Pro, DeepSource, GitHub Copilot Code Review, Code Climate, SonarCloud, Anthropic Claude Code Review — none publish per-prompt JBB-Behaviors benchmark logs or formal memory-isolation invariants for review agents (verified via their public docs as of 2026-05-17). Their internal product positioning varies; we make no per-vendor categorical claim here.";

export const COMPARISON_GRANITE_CALLOUT = {
  title: "Granite Guardian 4 — honest call-out",
  body:
    "We measured ourselves vs IBM Granite Guardian 4 on the same JBB-Behaviors n=80 holdout. Granite scores 98.75% block rate. Apohara scores 93.75% (Wilson [86.2%, 97.3%]) on the 9-vendor ensemble. Granite is a purpose-built single-vendor safety classifier. Apohara is 9-vendor adversarial consensus with formal memory isolation. Different products, different trade-offs.",
  interpretation:
    "A purpose-built classifier wins on its home turf benchmark. Apohara's value isn't 'beats Granite on JBB' — it's multi-vendor consensus (Granite is single-model and shares its blind spots across requests), formal KV-cache isolation (Granite has none), reproducible adversarial framework (Granite has internal claims but no published per-prompt logs), and availability isolation (Granite outage = total failure; Apohara routes through 9 providers).",
  measurementSource: "apohara-aegis/logs/granite4_jbb_n80_20260516T164541Z.json + apohara-aegis AUDIT.md entry #23 (commit cd1f439)",
};

export const WHY_THIS_MATTERS = {
  eyebrow: "Why this matters",
  title: "Three things this fixes that other tools don't.",

  multiVendor: {
    heading: "Why 9 vendors, not 1.",
    body:
      "Every LLM has shared blind spots across its own requests. If you ask Claude to review code Claude wrote, you get one vendor's worldview twice. We dispatch 9 frontier vendors in parallel — Claude, GPT, DeepSeek, Kimi, GLM, Qwen, Nemotron, MiniMax, Big Pickle — and aggregate their verdicts. The 93.75% block rate on JailbreakBench (apohara-aegis/logs/baseline_aegis-ensemble-10frontier_day5_FALLBACK_20260515T212737Z.json, Wilson [86.2%, 97.3%], n=80 holdout, 75 of 80 blocked) is what consensus buys you. Single-vendor review never gets there.",
  },

  inv15: {
    heading: "Why INV-15 (formal memory isolation).",
    body:
      "Multi-agent LLM pipelines share KV-cache by default. That means one attacker's prompt can poison another's session. INV-15 is the formal invariant we wrote and proved in our paper (DOI 10.5281/zenodo.20114594) — the JCRSafetyGate enforces dense-prefill mode under specific risk conditions, guaranteeing isolation between judge agents. Every verdict ledger entry includes a contextforge_audit_id that traces the gate decision. No competitor publishes anything like this.",
  },

  multiHardware: {
    heading: "Why H100 + MI300X.",
    body:
      "Single-vendor benchmarks live or die on a single hardware platform. We measured Apohara on both Nvidia H100 (5-agent baseline, US-014) and AMD Instinct MI300X across three waves — the most extreme being 65K-262K context length sweep (Apohara_Context_Forge/logs/mi300x_extreme_scale_1778977872.json). When a vendor benchmark only runs on the chip the vendor built, the result generalizes to nothing. Ours generalizes to two architectures with public log files.",
  },
};

export const CTA_FINAL_COPY = {
  title: "Verify your code now.",
  subtitle: "5 free calls/IP/day with the demo key — no signup. Or paste your own Gemini key for unlimited runs.",
};

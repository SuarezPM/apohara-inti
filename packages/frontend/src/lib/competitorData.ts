/** Typed competitor data for the Comparison section.
 *  Tier 1 = hackathon peers (full per-cell grading, low blowback risk).
 *  Tier 2 = commercial market players (narrative + chip list, no per-cell grading).
 *  Granite Guardian 4 = separate honest call-out (we measured them directly).
 *
 *  Data verified as of 2026-05-17. Apohara row cells link to specific
 *  artifacts (commit SHAs / log file paths / AUDIT entries). */

export type Tier1Cell = { value: string; source?: string };

export type Tier1Competitor = {
  name: string;
  highlighted?: boolean;
  vendors: Tier1Cell;
  tests: Tier1Cell;
  publicBenchmarks: Tier1Cell;
  multiHardware: Tier1Cell;
  formalInvariant: Tier1Cell;
  license: Tier1Cell;
  cost: Tier1Cell;
  source: { label: string; url: string };
};

/** Tier 1: 4 rows (Apohara + 3 hackathon peers). Fully cited per-cell. */
export const TIER_1: Tier1Competitor[] = [
  {
    name: "Apohara Inti",
    highlighted: true,
    vendors: {
      value: "9",
      source: "claude-opus-4.7, gpt-5.5, deepseek-v4-pro, kimi-k2.6, glm-5.1, qwen3.6-plus, nemotron-3-super-120b, minimax-m2.7, big-pickle (apohara-aegis/multi_judge.py)",
    },
    tests: {
      value: "150 funcs / 467 cases",
      source: "94 aegis def test_ funcs + 56 ctx-forge funcs (parametrize expansion: 94 aegis + 373 ctx-forge runtime = 467 per Apohara_Context_Forge/AUDIT.md line 469 '373 passed, 26 skipped')",
    },
    publicBenchmarks: {
      value: "JBB 93.75% / HarmBench 77.5%",
      source: "apohara-aegis/logs/baseline_aegis-ensemble-10frontier_day5_FALLBACK_20260515T212737Z.json — 75/80 blocked, Wilson 95% CI [86.2%, 97.3%]",
    },
    multiHardware: {
      value: "H100 + MI300X",
      source: "H100 5-agent US-014 + MI300X Wave A/B/C (Apohara_Context_Forge/logs/mi300x_extreme_scale_1778977872.json)",
    },
    formalInvariant: {
      value: "INV-15 (JCRSafetyGate)",
      source: "DOI 10.5281/zenodo.20114594 + Apohara_Context_Forge/apohara_context_forge/safety/jcr_gate.py",
    },
    license: { value: "Apache-2.0", source: "github.com/SuarezPM/apohara-inti/blob/main/LICENSE" },
    cost: {
      value: "Free + BYOK or 5/IP/day demo",
      source: "packages/backend/rate_limiter.py (DailyRateLimiter max_per_day=5, UTC rollover)",
    },
    source: { label: "github.com/SuarezPM/apohara-inti", url: "https://github.com/SuarezPM/apohara-inti" },
  },
  {
    name: "Pantheon",
    vendors: { value: "1 (Gemini 2.5 Flash)", source: "Pantheon backend single-vendor LLM call" },
    tests: { value: "0", source: "No test files in repo as of 2026-05-17" },
    publicBenchmarks: { value: "None published", source: "No measurement JSONs or benchmark docs" },
    multiHardware: { value: "Single CPU (Render)", source: "Render free-tier compute" },
    formalInvariant: { value: "None", source: "No formal invariant declared" },
    license: { value: "README says MIT, no LICENSE file", source: "GitHub metadata: License = None (inconsistency)" },
    cost: { value: "Free demo", source: "demo@pantheon.ai / pantheon2025" },
    source: { label: "github.com/umairyousif239/Pantheon", url: "https://github.com/umairyousif239/Pantheon" },
  },
  {
    name: "Vela",
    vendors: { value: "1 (Gemini 2.5 Flash)", source: "Vela README + Flask backend" },
    tests: { value: "0", source: "No test files in repo as of 2026-05-17" },
    publicBenchmarks: { value: "None published", source: "Sales page only" },
    multiHardware: { value: "Single Vultr droplet", source: "tryvela.io deployment" },
    formalInvariant: { value: "None", source: "Not declared" },
    license: { value: "No LICENSE file", source: 'GitHub metadata: License = None; footer says "© 2026 GitHub, Inc." (template artifact)' },
    cost: { value: "$49 / $99 / $199 per month", source: "tryvela.io pricing page" },
    source: { label: "tryvela.io", url: "https://tryvela.io/" },
  },
  {
    name: "Trusyn",
    vendors: { value: "1 (Gemini multi-variant, single-vendor)", source: "Trusyn AI Gateway → Gemini family with circuit breaker + fallback" },
    tests: { value: "0", source: "No test files visible in 5-commit history" },
    publicBenchmarks: { value: "None published", source: "v0.1.0 prototype phase" },
    multiHardware: { value: "Single Vercel deploy", source: "trusyn-public.vercel.app" },
    formalInvariant: { value: "None", source: "Not declared" },
    license: { value: "Apache-2.0", source: "Repo LICENSE" },
    cost: { value: "Not specified", source: "No pricing page" },
    source: { label: "github.com/Trusyn-AI/trusyn-ai", url: "https://github.com/Trusyn-AI/trusyn-ai" },
  },
];

/** Tier 2: commercial market players. Listed as a single narrative chip + name list.
 *  No per-cell grading — see editorialCopy.COMPARISON_TIER2_NARRATIVE for rationale. */
export const TIER_2 = [
  { name: "Snyk Code", url: "https://snyk.io/product/snyk-code/" },
  { name: "Semgrep Pro", url: "https://semgrep.dev/products/semgrep-code/" },
  { name: "DeepSource", url: "https://deepsource.io/" },
  { name: "GitHub Copilot Code Review", url: "https://github.com/features/copilot/code-review" },
  { name: "Code Climate", url: "https://codeclimate.com/quality" },
  { name: "SonarCloud", url: "https://www.sonarsource.com/products/sonarcloud/" },
  { name: "Anthropic Claude Code Review", url: "https://www.anthropic.com/claude-code" },
];

/** Granite Guardian 4: separate honest call-out with measured H2H. */
export const GRANITE = {
  apohara: "93.75% block rate (Wilson [86.2%, 97.3%])",
  granite: "98.75% block rate",
  measurementUrl:
    "https://github.com/SuarezPM/apohara-aegis/blob/main/logs/granite4_jbb_n80_20260516T164541Z.json",
  auditUrl:
    "https://github.com/SuarezPM/apohara-aegis/blob/main/AUDIT.md",
  auditCommit: "cd1f439",
  productLink: { label: "ibm.com/granite", url: "https://www.ibm.com/granite" },
};

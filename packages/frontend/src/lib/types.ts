// Shared TypeScript types for the Apohara PROBANT frontend.
// Mirrors the shape backend US-006 will emit from POST /v1/verify.

export type Vendor = {
  /** Display name shown in the AttackerCard header (e.g. "Claude Opus 4.7"). */
  name: string;
  /** Underlying model identifier (e.g. "anthropic/claude-opus-4-7"). */
  model: string;
  /** Routing gateway: "opencode Zen" | "OpenRouter" | "direct". */
  gateway: string;
  /** Two-letter accent code used for the styled badge when no logo is available. */
  badge: string;
  /** Backend seat label (e.g. "claude-opus-47-seat"); used by the response adapter
   *  to map backend AttackerReport entries back to their Vendor card. */
  seat: string;
};

export type AttackerStatus = "pending" | "running" | "ok" | "error" | "fail_open";

export type AttackerResult = {
  vendor: Vendor;
  status: AttackerStatus;
  /** True when the attacker flagged the code as risky/jailbroken/unsafe. */
  found_issue: boolean;
  /** Short reasoning snippet (full text in `details`). */
  reasoning: string;
  /** Optional latency in ms for observability. */
  latency_ms?: number;
  /** Optional full details payload (truncated by UI for the card snippet). */
  details?: string;
};

export type Verdict = "verified" | "risky" | "blocked";

export type JCRDecision = {
  /** ContextForge JCRSafetyGate decision tag (INV-15 enforcement layer). */
  decision: "allow" | "deny" | "review";
  /** ContextForge audit id, signed by the memory-plane keypair. */
  audit_id: string;
  /** ISO-8601 timestamp when the gate emitted the decision. */
  timestamp: string;
  /** ContextForge invariant id; always "INV-15" for this product. */
  invariant: string;
  /** Optional reason string surfaced from the safety gate. */
  reason?: string;
};

export type VerdictResponse = {
  verdict: Verdict;
  /** 0..9 — number of attackers that flagged a problem. */
  found_issue_count: number;
  /** Always 9 in the current product spec. */
  attacker_count: number;
  /** One result per attacker, ordered to match the UI grid. */
  attackers: AttackerResult[];
  /** Human-readable reasoning summary (3-5 sentences). */
  reasoning_summary: string;
  /** ContextForge JCR decision — proof memory isolation held. */
  jcr_decision: JCRDecision;
  /** Link to the signed audit trail blob (jsonl over HTTPS). */
  signed_audit_trail_url: string;
};

export type VerifyRequest = {
  /** User-supplied Gemini API key (BYOK; never persisted server-side). */
  gemini_api_key: string;
  /** Code, diff, PR URL, or task description to verify. */
  code: string;
};

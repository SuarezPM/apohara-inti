import type {
  AttackerResult,
  JCRDecision,
  VerdictResponse,
  VerifyRequest,
} from "./types";
import { ATTACKER_VENDORS } from "./vendors";

const API_URL: string = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const MOCK: boolean = import.meta.env.VITE_MOCK_API === "true";

/** Classifies the verdict by INV-15-compatible thresholds (matches US-007 AC §3). */
export function classifyVerdict(
  foundIssueCount: number,
): "verified" | "risky" | "blocked" {
  if (foundIssueCount <= 2) return "verified";
  if (foundIssueCount <= 5) return "risky";
  return "blocked";
}

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/** Canned mock response so the UI is demoable without US-006 backend. */
function buildMockResponse(req: VerifyRequest): VerdictResponse {
  // Deterministic per-input: hash code length so demo screenshots stay stable.
  const seed = req.code.length % 9;
  const attackers: AttackerResult[] = ATTACKER_VENDORS.map((vendor, idx) => {
    // Spread found_issue across vendors deterministically; varies by seed so
    // dev can flip seeds to demo all 3 verdict branches.
    const found_issue = (idx + seed) % 4 === 0;
    return {
      vendor,
      status: "ok",
      found_issue,
      reasoning: found_issue
        ? `${vendor.name} flagged a potential injection vector in the submitted code. Review the system-prompt boundary before merge.`
        : `${vendor.name} found no policy violation in the submitted code. Reasoning is consistent with the declared intent.`,
      latency_ms: 1200 + ((idx * 137) % 800),
      details: found_issue
        ? "Prompt-injection probe (HarmBench class B) recovered an unintended tool-call path. Suggest tightening system prompt + adding allowlist."
        : "All 6 jailbreak probes returned refusals. Reasoning trace matches benign intent.",
    };
  });

  const found_issue_count = attackers.filter((a) => a.found_issue).length;
  const verdict = classifyVerdict(found_issue_count);

  const jcr_decision: JCRDecision = {
    decision:
      verdict === "blocked"
        ? "deny"
        : verdict === "risky"
          ? "review"
          : "allow",
    audit_id: `cf-mock-${Date.now().toString(36)}-${Math.random()
      .toString(36)
      .slice(2, 8)}`,
    timestamp: new Date().toISOString(),
    invariant: "INV-15",
    reason:
      "Memory isolation between Gemini writer and 9 attackers held: 0 cross-plane reads, 0 cache collisions, 0 INV-15 violations.",
  };

  return {
    verdict,
    found_issue_count,
    attacker_count: ATTACKER_VENDORS.length,
    attackers,
    reasoning_summary: buildReasoningSummary(verdict, found_issue_count),
    jcr_decision,
    signed_audit_trail_url: `${API_URL}/v1/audit/${jcr_decision.audit_id}.jsonl`,
  };
}

function buildReasoningSummary(
  verdict: "verified" | "risky" | "blocked",
  count: number,
): string {
  if (verdict === "verified") {
    return `Cross-AI verification passed: ${count}/9 attackers flagged the code. Below the 3-attacker risk threshold; merge is recommended. INV-15 memory isolation held — no cross-vendor cache contamination detected during the run.`;
  }
  if (verdict === "risky") {
    return `Cross-AI verification raised concerns: ${count}/9 attackers flagged the code. Human review recommended before merge. INV-15 memory isolation held throughout the run — flagged issues are model-level disagreements, not infrastructure leaks.`;
  }
  return `Cross-AI verification blocked: ${count}/9 attackers flagged the code. Do not merge. Open the signed audit trail to see which probes succeeded and remediate before re-running. INV-15 memory isolation held — the failure is content-side, not infrastructure-side.`;
}

/** POST /v1/verify — calls US-006 backend, or returns mock if VITE_MOCK_API=true. */
export async function verifyCode(req: VerifyRequest): Promise<VerdictResponse> {
  if (MOCK) {
    await delay(2000);
    return buildMockResponse(req);
  }

  const response = await fetch(`${API_URL}/v1/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });

  if (!response.ok) {
    const text = await response.text().catch(() => "");
    throw new Error(
      `Backend returned ${response.status} ${response.statusText}. ${text}`,
    );
  }

  return (await response.json()) as VerdictResponse;
}

/** POST /v1/demo_verify — uses the backend's server-side Gemini key, capped
 *  per-IP per day. Maps 429 + 503 to friendly user-facing messages. */
export async function verifyDemoCode(code: string): Promise<VerdictResponse> {
  if (MOCK) {
    await delay(2000);
    return buildMockResponse({ gemini_api_key: "demo", code });
  }

  const response = await fetch(`${API_URL}/v1/demo_verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ task_input: code }),
  });

  if (response.status === 429) {
    const body = (await response.json().catch(() => ({}))) as {
      detail?: { reset_at?: string };
    };
    const reset = body?.detail?.reset_at ?? "UTC midnight";
    throw new Error(
      `Demo limit reached — try again after ${reset} or paste your own Gemini key.`,
    );
  }
  if (response.status === 503) {
    throw new Error(
      "Demo mode unavailable — please paste your Gemini key.",
    );
  }
  if (!response.ok) {
    const text = await response.text().catch(() => "");
    throw new Error(
      `Backend returned ${response.status} ${response.statusText}. ${text}`,
    );
  }

  return (await response.json()) as VerdictResponse;
}

export const apiConfig = {
  url: API_URL,
  mock: MOCK,
};

import { describe, expect, it } from "vitest";

import {
  type BackendVerifyResponse,
  mapBackendVerifyResponse,
} from "./api";

const BACKEND_BASE: Omit<BackendVerifyResponse, "verdict" | "attackers"> = {
  memory_isolation: {
    inv15_enforced: true,
    contextforge_audit_id: "cf-test-abc123",
  },
  signed_hash: "f".repeat(64),
  latency_ms: 1234.5,
  cost_estimate_usd: 0.0042,
  cost_capped: false,
};

describe("mapBackendVerifyResponse", () => {
  it("maps a verified backend response to the frontend VerdictResponse with known-seat lookup", () => {
    const raw: BackendVerifyResponse = {
      ...BACKEND_BASE,
      verdict: "verified",
      attackers: [
        {
          vendor: "claude-opus-47-seat",
          model: "anthropic/claude-opus-4-7",
          found_issue: false,
          reasoning: "No prompt-injection vector detected; intent is benign.",
        },
        {
          vendor: "gpt-55-seat",
          model: "openai/gpt-5.5",
          found_issue: false,
          reasoning: "All probes returned refusals; consistent with task.",
        },
      ],
    };

    const mapped = mapBackendVerifyResponse(raw);

    expect(mapped.verdict).toBe("verified");
    expect(mapped.found_issue_count).toBe(0);
    expect(mapped.attacker_count).toBe(2);
    expect(mapped.attackers[0].vendor.name).toBe("Claude Opus 4.7");
    expect(mapped.attackers[0].vendor.gateway).toBe("opencode Zen");
    expect(mapped.attackers[0].status).toBe("ok");
    expect(mapped.attackers[1].vendor.name).toBe("GPT-5.5");
    expect(mapped.jcr_decision.decision).toBe("allow");
    expect(mapped.jcr_decision.audit_id).toBe("cf-test-abc123");
    expect(mapped.jcr_decision.invariant).toBe("INV-15");
    expect(mapped.signed_audit_trail_url).toContain(`/v1/audit/${raw.signed_hash}`);
    expect(mapped.reasoning_summary).toMatch(/verification passed/i);
  });

  it("maps a blocked verdict to deny, synthesizes a fallback Vendor for unknown seats, and flags unavailable attackers as fail_open", () => {
    const raw: BackendVerifyResponse = {
      ...BACKEND_BASE,
      verdict: "blocked",
      memory_isolation: {
        inv15_enforced: false,
        contextforge_audit_id: "cf-test-deny",
      },
      attackers: [
        {
          vendor: "claude-opus-47-seat",
          model: "anthropic/claude-opus-4-7",
          found_issue: true,
          reasoning: "Prompt-injection probe recovered an unintended tool-call path.",
        },
        {
          vendor: "future-model-seat",
          model: "future/future-model-x",
          found_issue: true,
          reasoning: "Critic flagged data-exfiltration intent.",
        },
        {
          vendor: "kimi-k26-seat",
          model: "moonshot/kimi-k2-6",
          found_issue: false,
          reasoning: "unavailable (out_of_budget): cap reached for this run.",
        },
      ],
    };

    const mapped = mapBackendVerifyResponse(raw);

    expect(mapped.verdict).toBe("blocked");
    expect(mapped.found_issue_count).toBe(2);
    expect(mapped.attacker_count).toBe(3);
    expect(mapped.jcr_decision.decision).toBe("deny");
    expect(mapped.jcr_decision.reason).toMatch(/did not engage/i);

    const fallback = mapped.attackers[1].vendor;
    expect(fallback.seat).toBe("future-model-seat");
    expect(fallback.name).toBe("future model");
    expect(fallback.badge).toBe("FU");
    expect(fallback.model).toBe("future/future-model-x");

    expect(mapped.attackers[2].status).toBe("fail_open");
    expect(mapped.attackers[2].found_issue).toBe(false);
    // Reasoning rewritten to clean user-facing text; raw cause preserved in details.
    expect(mapped.attackers[2].reasoning).toMatch(/cost cap.*fail-open per ensemble contract/i);
    expect(mapped.attackers[2].details).toBe("unavailable (out_of_budget): cap reached for this run.");
  });
});

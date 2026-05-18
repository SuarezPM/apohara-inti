import { useCallback, useMemo, useRef, useState } from "react";
import { Loader2, Sparkles } from "lucide-react";
import { ApiKeyInput } from "@/components/ApiKeyInput";
import { CodeInput } from "@/components/CodeInput";
import { AttackerGrid } from "@/components/AttackerGrid";
import { MemoryPlaneIndicator } from "@/components/MemoryPlaneIndicator";
import { VerdictPanel } from "@/components/VerdictPanel";
import { ErrorBanner } from "@/components/ErrorBanner";
import { Button } from "@/components/ui/button";
import { verifyCode, verifyDemoCode, mapBackendVerifyResponse } from "@/lib/api";
import type { BackendVerifyResponse } from "@/lib/api";
import { verifyStream } from "@/lib/streamingVerify";
import { ATTACKER_VENDORS } from "@/lib/vendors";
import type { AttackerResult, VerdictResponse } from "@/lib/types";

const API_URL: string = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export function TryItPanel() {
  const [apiKey, setApiKey] = useState("");
  const [code, setCode] = useState("");
  const [isVerifying, setIsVerifying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errorVariant, setErrorVariant] = useState<"destructive" | "info">("destructive");
  const [response, setResponse] = useState<VerdictResponse | null>(null);
  const [demoMode, setDemoMode] = useState(false);
  const [streamMode, setStreamMode] = useState(false);
  // Incremental attacker results for streaming mode
  const [streamingAttackers, setStreamingAttackers] = useState<AttackerResult[]>([]);
  const abortRef = useRef<AbortController | null>(null);

  const canVerify = useMemo(
    () =>
      code.trim().length > 0 &&
      !isVerifying &&
      (demoMode || apiKey.trim().length > 0),
    [apiKey, code, isVerifying, demoMode],
  );

  // Batch (non-streaming) path — existing behaviour preserved.
  const handleVerifyBatch = useCallback(async () => {
    setError(null);
    setErrorVariant("destructive");
    setResponse(null);
    setStreamingAttackers([]);
    setIsVerifying(true);
    try {
      const result = demoMode
        ? await verifyDemoCode(code.trim())
        : await verifyCode({
            gemini_api_key: apiKey.trim(),
            code: code.trim(),
          });
      setResponse(result);
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Verification failed. Check the backend is reachable and try again.";
      const info = /demo mode unavailable|demo limit reached/i.test(message);
      setErrorVariant(info ? "info" : "destructive");
      setError(message);
    } finally {
      setIsVerifying(false);
    }
  }, [apiKey, code, demoMode]);

  // Streaming path — yields per-vendor events incrementally.
  const handleVerifyStream = useCallback(async () => {
    setError(null);
    setErrorVariant("destructive");
    setResponse(null);

    // Pre-populate all 9 cards in "running" state.
    const runningAttackers: AttackerResult[] = ATTACKER_VENDORS.map((vendor) => ({
      vendor,
      status: "running" as const,
      found_issue: false,
      reasoning: "",
    }));
    setStreamingAttackers(runningAttackers);
    setIsVerifying(true);

    const ctrl = new AbortController();
    abortRef.current = ctrl;

    try {
      const body = demoMode
        ? { task_input: code.trim() }
        : { task_input: code.trim(), gemini_api_key: apiKey.trim() };

      const gen = verifyStream(API_URL, body, ctrl.signal);

      for await (const ev of gen) {
        if (ev.event === "vendor_completed") {
          const d = ev.data as {
            vendor: string;
            model: string;
            found_issue: boolean;
            reasoning: string;
          };
          setStreamingAttackers((prev) => {
            const updated = [...prev];
            // Match by vendor seat name (backend emits seat label as "vendor").
            const idx = updated.findIndex(
              (a) => a.vendor.seat === d.vendor,
            );
            if (idx !== -1) {
              updated[idx] = {
                ...updated[idx],
                status: "ok",
                found_issue: d.found_issue,
                reasoning: d.reasoning,
              };
            }
            return updated;
          });
        } else if (ev.event === "all_done") {
          const raw = ev.data as BackendVerifyResponse;
          setResponse(mapBackendVerifyResponse(raw));
          // Mark any still-running cards as ok (e.g. DPI short-circuit: 0 vendors).
          setStreamingAttackers((prev) =>
            prev.map((a) =>
              a.status === "running" ? { ...a, status: "ok" as const } : a,
            ),
          );
        } else if (ev.event === "error") {
          const d = ev.data as { detail?: string };
          throw new Error(d.detail ?? "Streaming verification error");
        }
      }
    } catch (err) {
      if (err instanceof Error && err.name === "AbortError") return;
      const message =
        err instanceof Error
          ? err.message
          : "Streaming verification failed. Check the backend is reachable.";
      const info = /demo mode unavailable|demo limit reached/i.test(message);
      setErrorVariant(info ? "info" : "destructive");
      setError(message);
      // Mark remaining running cards as error.
      setStreamingAttackers((prev) =>
        prev.map((a) =>
          a.status === "running" ? { ...a, status: "error" as const } : a,
        ),
      );
    } finally {
      setIsVerifying(false);
      abortRef.current = null;
    }
  }, [apiKey, code, demoMode]);

  const handleVerify = useCallback(async () => {
    if (!canVerify) return;
    if (streamMode) {
      await handleVerifyStream();
    } else {
      await handleVerifyBatch();
    }
  }, [canVerify, streamMode, handleVerifyStream, handleVerifyBatch]);

  // Effective attacker list: streaming incremental results or final batch results.
  const effectiveAttackers = streamMode && streamingAttackers.length > 0
    ? streamingAttackers
    : response?.attackers;

  return (
    <section id="try" className="border-b border-border/40 py-16 lg:py-24" aria-labelledby="try-title">
      <div className="container max-w-6xl">
        <header className="max-w-2xl mb-10">
          <p className="font-mono text-[10px] text-primary uppercase tracking-widest mb-2">
            Try it live
          </p>
          <h2 id="try-title" className="font-pixel-sans text-lg sm:text-xl lg:text-2xl text-foreground leading-tight whitespace-nowrap">
            Paste code &rarr; verify in 30s.
          </h2>
          <p className="mt-3 text-sm text-muted-foreground">
            Bring your own Gemini key or hit the shared demo key (5 calls/IP/UTC day).
            Backend lives at <code className="font-mono text-primary">api.apohara.dev</code>.
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <ApiKeyInput
            value={apiKey}
            onChange={setApiKey}
            disabled={isVerifying}
            demoActive={demoMode}
            onToggleDemo={() => setDemoMode((prev) => !prev)}
          />
          <CodeInput value={code} onChange={setCode} disabled={isVerifying} />
        </div>

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 mb-6">
          <div className="flex flex-col gap-1.5">
            <p className="text-xs text-muted-foreground max-w-xl">
              Gemini writes/audits. 9 frontier vendors adversarially attack. Apohara
              ContextForge enforces memory isolation (INV-15) between every plane.
            </p>
            <label className="inline-flex items-center gap-2 cursor-pointer select-none w-fit">
              <input
                type="checkbox"
                checked={streamMode}
                onChange={(e) => setStreamMode(e.target.checked)}
                disabled={isVerifying}
                className="accent-primary h-3.5 w-3.5"
                aria-label="Stream live vendor results (experimental)"
              />
              <span className="font-mono text-[10px] text-muted-foreground">
                Stream live vendor results (experimental)
              </span>
            </label>
          </div>
          <Button
            type="button"
            size="lg"
            disabled={!canVerify}
            onClick={handleVerify}
            variant="default"
            className="font-pixel-sans text-[11px] tracking-wider min-w-[180px]"
          >
            {isVerifying ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Verifying...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                Verify
              </>
            )}
          </Button>
        </div>

        {error && (
          <div className="mb-6">
            <ErrorBanner
              message={error}
              onDismiss={() => setError(null)}
              variant={errorVariant}
            />
          </div>
        )}

        <div className="space-y-6">
          <MemoryPlaneIndicator
            active={isVerifying}
            decision={response?.jcr_decision}
          />

          <div>
            <header className="flex items-baseline justify-between mb-3">
              <h3 className="font-pixel-sans text-sm text-foreground">Defense Plane &mdash; 9 attackers</h3>
              <p className="font-mono text-[10px] text-muted-foreground">
                {response
                  ? `${response.found_issue_count} of ${response.attacker_count} flagged an issue`
                  : isVerifying && streamMode
                    ? `${streamingAttackers.filter((a) => a.status === "ok").length} of 9 completed`
                    : "Awaiting verification"}
              </p>
            </header>
            <AttackerGrid results={effectiveAttackers} />
          </div>

          {response && <VerdictPanel response={response} />}
        </div>
      </div>
    </section>
  );
}

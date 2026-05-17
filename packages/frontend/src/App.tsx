import { useMemo, useState } from "react";
import { Loader2, ShieldHalf, Sparkles } from "lucide-react";
import { ApiKeyInput } from "@/components/ApiKeyInput";
import { CodeInput } from "@/components/CodeInput";
import { AttackerGrid } from "@/components/AttackerGrid";
import { MemoryPlaneIndicator } from "@/components/MemoryPlaneIndicator";
import { VerdictPanel } from "@/components/VerdictPanel";
import { ErrorBanner } from "@/components/ErrorBanner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { apiConfig, verifyCode, verifyDemoCode } from "@/lib/api";
import type { VerdictResponse } from "@/lib/types";

export default function App() {
  const [apiKey, setApiKey] = useState("");
  const [code, setCode] = useState("");
  const [isVerifying, setIsVerifying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<VerdictResponse | null>(null);
  const [demoMode, setDemoMode] = useState(false);

  const canVerify = useMemo(
    () =>
      code.trim().length > 0 &&
      !isVerifying &&
      (demoMode || apiKey.trim().length > 0),
    [apiKey, code, isVerifying, demoMode],
  );

  const handleVerify = async () => {
    if (!canVerify) return;
    setError(null);
    setResponse(null);
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
      setError(message);
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <div className="min-h-screen">
      <header className="border-b border-border/70">
        <div className="container flex items-center justify-between gap-4 py-4">
          <div className="flex items-center gap-3">
            <span className="inline-flex h-9 w-9 items-center justify-center rounded-md bg-primary/15 text-primary">
              <ShieldHalf className="h-5 w-5" />
            </span>
            <div>
              <h1 className="text-base font-semibold leading-none">
                Apohara Inti
              </h1>
              <p className="mt-1 text-xs text-muted-foreground">
                A different AI reviews the code your AI just wrote, while your
                agent memory stays isolated.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {apiConfig.mock && (
              <Badge variant="outline" className="border-plane-defense/50 text-plane-defense">
                MOCK MODE
              </Badge>
            )}
            <Badge variant="secondary" className="font-mono">
              {apiConfig.url}
            </Badge>
          </div>
        </div>
      </header>

      <main className="container max-w-6xl space-y-6 py-6">
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <ApiKeyInput
            value={apiKey}
            onChange={setApiKey}
            disabled={isVerifying}
            demoActive={demoMode}
            onToggleDemo={() => setDemoMode((prev) => !prev)}
          />
          <CodeInput value={code} onChange={setCode} disabled={isVerifying} />
        </section>

        <section className="flex flex-col items-center gap-3 sm:flex-row sm:justify-between">
          <p className="text-xs text-muted-foreground">
            Gemini writes/audits. 9 frontier vendors adversarially attack. Apohara
            ContextForge enforces memory isolation (INV-15) between every plane.
          </p>
          <Button
            type="button"
            size="lg"
            disabled={!canVerify}
            onClick={handleVerify}
            className="min-w-[180px]"
          >
            {isVerifying ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Verifying…
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                Verify
              </>
            )}
          </Button>
        </section>

        {error && (
          <ErrorBanner
            message={error}
            onDismiss={() => setError(null)}
          />
        )}

        <section aria-label="Memory plane status">
          <MemoryPlaneIndicator
            active={isVerifying}
            decision={response?.jcr_decision}
          />
        </section>

        <section
          aria-label="9 cross-vendor adversarial attackers"
          className="space-y-3"
        >
          <header className="flex items-baseline justify-between">
            <h2 className="text-sm font-semibold">Defense Plane — 9 Attackers</h2>
            <p className="text-xs text-muted-foreground">
              {response
                ? `${response.found_issue_count} of ${response.attacker_count} flagged an issue`
                : "Awaiting verification"}
            </p>
          </header>
          <AttackerGrid results={response?.attackers} />
        </section>

        {response && (
          <section aria-label="Verdict">
            <VerdictPanel response={response} />
          </section>
        )}

        <footer className="border-t border-border/70 pt-4 text-xs text-muted-foreground">
          <p>
            Apohara Inti — Apache-2.0 OSS. ContextForge powers the memory plane;
            Apohara Aegis powers the defense plane. Audit blobs are
            signed and reproducible. BYOK Gemini key; 9 attackers run on Apohara
            credits.
          </p>
        </footer>
      </main>
    </div>
  );
}

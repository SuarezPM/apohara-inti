import { useEffect, useState } from "react";

interface LedgerEntry {
  verdict: "verified" | "risky" | "blocked";
  attackers: Array<{
    vendor: string;
    model: string;
    found_issue: boolean;
    reasoning: string;
  }>;
  signed_hash: string;
  latency_ms: number;
  ts: number;
}

export function Dashboard() {
  const [entries, setEntries] = useState<LedgerEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [adminKey, setAdminKey] = useState<string>(
    () => localStorage.getItem("apohara_admin_key") ?? "",
  );

  useEffect(() => {
    if (!adminKey) return;

    const fetchData = async () => {
      try {
        const params = new URLSearchParams({ limit: "50", admin_key: adminKey });
        const resp = await fetch(
          `https://api.apohara.dev/v1/audit/recent?${params.toString()}`,
        );
        if (!resp.ok) {
          setError(`HTTP ${resp.status}`);
          return;
        }
        const data = (await resp.json()) as { entries: LedgerEntry[] };
        setEntries(data.entries ?? []);
        setError(null);
      } catch (e) {
        setError((e as Error).message);
      }
    };

    void fetchData();
    const interval = setInterval(() => void fetchData(), 5000);
    return () => clearInterval(interval);
  }, [adminKey]);

  if (!adminKey) {
    return (
      <div className="container mx-auto py-12 max-w-md">
        <h1 className="text-2xl font-pixel-sans mb-4">PROBANT Dashboard — Admin Access</h1>
        <input
          type="password"
          placeholder="APOHARA_ADMIN_KEY"
          className="w-full p-2 border border-border bg-card text-foreground rounded"
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              const val = (e.target as HTMLInputElement).value;
              localStorage.setItem("apohara_admin_key", val);
              setAdminKey(val);
            }
          }}
        />
        <p className="text-sm text-muted-foreground mt-2">
          Press Enter to set. Stored in localStorage. To revoke: clear browser storage.
        </p>
      </div>
    );
  }

  const counts = entries.reduce(
    (acc, e) => {
      acc[e.verdict] = (acc[e.verdict] ?? 0) + 1;
      return acc;
    },
    { verified: 0, risky: 0, blocked: 0 } as Record<string, number>,
  );
  const total = entries.length || 1;

  return (
    <div className="container mx-auto py-12">
      <h1 className="text-3xl font-pixel-sans mb-6">PROBANT Dashboard</h1>

      {error && (
        <div className="p-4 bg-destructive text-destructive-foreground rounded mb-4 font-mono text-sm">
          Error: {error}
        </div>
      )}

      {/* Verdict trend bar */}
      <div className="mb-8">
        <h2 className="text-xl mb-2">
          Verdict distribution{" "}
          <span className="text-muted-foreground text-base font-normal">
            (last {entries.length})
          </span>
        </h2>
        <div className="flex h-8 w-full rounded overflow-hidden border border-border">
          <div
            className="bg-primary transition-all"
            style={{ width: `${(counts.verified / total) * 100}%` }}
            title={`verified: ${counts.verified}`}
          />
          <div
            className="bg-yellow-600 transition-all"
            style={{ width: `${(counts.risky / total) * 100}%` }}
            title={`risky: ${counts.risky}`}
          />
          <div
            className="bg-destructive transition-all"
            style={{ width: `${(counts.blocked / total) * 100}%` }}
            title={`blocked: ${counts.blocked}`}
          />
        </div>
        <div className="flex gap-4 mt-2 text-sm font-mono">
          <span className="text-primary">● verified {counts.verified}</span>
          <span className="text-yellow-600">● risky {counts.risky}</span>
          <span className="text-destructive">● blocked {counts.blocked}</span>
        </div>
      </div>

      {/* Recent verdicts table */}
      <h2 className="text-xl mb-2">Recent verdicts</h2>
      {entries.length === 0 ? (
        <p className="text-muted-foreground font-mono text-sm">No entries yet.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm font-mono">
            <thead>
              <tr className="border-b border-border text-left">
                <th className="p-2">Time (UTC)</th>
                <th className="p-2">Verdict</th>
                <th className="p-2">Attackers</th>
                <th className="p-2">Latency</th>
                <th className="p-2">Signed hash</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((e) => (
                <tr key={e.signed_hash} className="border-b border-border/40 hover:bg-card/60">
                  <td className="p-2 text-muted-foreground">
                    {new Date(e.ts * 1000).toISOString().slice(11, 19)}
                  </td>
                  <td
                    className={`p-2 font-semibold ${
                      e.verdict === "verified"
                        ? "text-primary"
                        : e.verdict === "risky"
                          ? "text-yellow-600"
                          : "text-destructive"
                    }`}
                  >
                    {e.verdict}
                  </td>
                  <td className="p-2">{e.attackers.length}</td>
                  <td className="p-2">{e.latency_ms.toFixed(0)}ms</td>
                  <td className="p-2 text-muted-foreground" title={e.signed_hash}>
                    {e.signed_hash.slice(0, 16)}…
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

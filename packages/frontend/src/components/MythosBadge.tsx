import { useState, useEffect, useRef } from "react";

// Matches the const BASE convention used across the SOAR dashboard sections
// (IncidentsPage/LiveFeedPage/JudgeLayerPage/CompliancePage/Dashboard). Hardcoded
// to the production droplet host because Vercel serves apohara.dev (origin) while
// the API lives at api.apohara.dev (different origin) — relative paths would 404
// on Vercel's SPA-rewrite catch-all.
const API_BASE = "https://api.apohara.dev";
const GITHUB_BASE = "https://github.com/SuarezPM/apohara-probant/blob/main";
const MYTHOS_STATUS_URL = `${API_BASE}/v1/soar/mythos/status`;

interface MythosStatus {
  enabled: boolean;
  reserved: boolean;
  status: string;
  activation_path: string;
  boundary_text_ref: string;
}

interface MythosBadgeProps {
  /** Render inline without the sidebar-bottom container padding */
  compact?: boolean;
}

export function MythosBadge({ compact = false }: MythosBadgeProps) {
  const [showModal, setShowModal] = useState(false);
  const [mythosData, setMythosData] = useState<MythosStatus | null>(null);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [showTooltip, setShowTooltip] = useState(false);
  const tooltipTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Fetch status on mount (used when modal opens)
  useEffect(() => {
    fetch(MYTHOS_STATUS_URL)
      .then((r) => r.json())
      .then((d: MythosStatus) => setMythosData(d))
      .catch((err) => setFetchError(String(err)));
  }, []);

  // Keyboard: Escape closes modal
  useEffect(() => {
    if (!showModal) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") setShowModal(false);
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [showModal]);

  const handleMouseEnter = () => {
    if (tooltipTimeout.current) clearTimeout(tooltipTimeout.current);
    setShowTooltip(true);
  };

  const handleMouseLeave = () => {
    tooltipTimeout.current = setTimeout(() => setShowTooltip(false), 150);
  };

  const badgeContent = (
    <div
      role="button"
      tabIndex={0}
      aria-label="MYTHOS-READY architecture badge — click for details"
      onClick={() => setShowModal(true)}
      onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); setShowModal(true); } }}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onFocus={handleMouseEnter}
      onBlur={handleMouseLeave}
      className={[
        "relative inline-flex items-center gap-1.5 cursor-pointer select-none",
        "rounded border px-2.5 py-1 font-mono text-[10px] font-semibold tracking-widest",
        "transition-all duration-150",
        "focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-1",
      ].join(" ")}
      style={{
        backgroundColor: "var(--apohara-ink)",
        borderColor: "var(--apohara-lime)",
        color: "var(--apohara-lime)",
        // ring offset colour matches dark sidebar
        "--tw-ring-color": "var(--apohara-lime)",
        "--tw-ring-offset-color": "var(--apohara-bg-mid)",
      } as React.CSSProperties}
    >
      <span aria-hidden="true" style={{ fontSize: "0.9em" }}>🔱</span>
      MYTHOS-READY

      {/* Tooltip */}
      {showTooltip && (
        <div
          role="tooltip"
          className="absolute bottom-full left-0 mb-2 z-50 w-72 rounded border p-2 text-[9px] leading-relaxed font-mono font-normal shadow-lg"
          style={{
            backgroundColor: "var(--apohara-bg-raised)",
            borderColor: "var(--apohara-lime)",
            color: "var(--apohara-bone)",
          }}
        >
          Architecture reserved for Claude Mythos via Project Glasswing / Claude
          for Open Source program. NOT yet active. Click for details.
        </div>
      )}
    </div>
  );

  if (compact) return (
    <>
      {badgeContent}
      {showModal && <MythosModal data={mythosData} error={fetchError} onClose={() => setShowModal(false)} />}
    </>
  );

  return (
    <div className="mx-2 mb-4">
      {badgeContent}
      {showModal && <MythosModal data={mythosData} error={fetchError} onClose={() => setShowModal(false)} />}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Modal

interface ModalProps {
  data: MythosStatus | null;
  error: string | null;
  onClose: () => void;
}

function MythosModal({ data, error, onClose }: ModalProps) {
  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Mythos architecture status"
      className="fixed inset-0 z-[200] flex items-center justify-center p-4"
      style={{ backgroundColor: "rgba(0,0,0,0.7)" }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div
        className="relative w-full max-w-lg rounded-md border p-5 shadow-2xl overflow-y-auto max-h-[90vh] font-mono text-xs"
        style={{
          backgroundColor: "var(--apohara-bg-void)",
          borderColor: "var(--apohara-lime)",
          color: "var(--apohara-bone)",
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h2
            className="font-pixel-sans text-sm tracking-widest uppercase"
            style={{ color: "var(--apohara-lime)" }}
          >
            🔱 MYTHOS-READY
          </h2>
          <button
            aria-label="Close modal"
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground transition-colors p-1 rounded focus:outline-none focus-visible:ring-2"
            style={{ "--tw-ring-color": "var(--apohara-lime)" } as React.CSSProperties}
          >
            ✕
          </button>
        </div>

        {/* Boundary text */}
        <p className="mb-4 leading-relaxed opacity-80 text-[10px]">
          Architecture reserved for Claude Mythos via Project Glasswing / Claude for Open Source program
          (application pending). <strong style={{ color: "var(--apohara-bone)" }}>NOT yet active.</strong>{" "}
          The <code>mythos_attacker_slot</code> activates only upon program approval and provisioning of
          legitimate API credentials. This does not claim Anthropic endorsement or access.
        </p>

        {/* Live status from /v1/soar/mythos/status */}
        <div
          className="rounded border p-3 mb-4"
          style={{ borderColor: "rgba(37,177,63,0.3)", backgroundColor: "var(--apohara-bg-raised)" }}
        >
          <p className="font-pixel-sans text-[8px] uppercase tracking-widest mb-2" style={{ color: "var(--apohara-lime)" }}>
            Live status — /v1/soar/mythos/status
          </p>
          {error ? (
            <p className="opacity-50 text-[10px]">Could not fetch status: {error}</p>
          ) : data ? (
            <dl className="space-y-1 text-[10px]">
              <div className="flex gap-2"><dt className="opacity-50 w-28 shrink-0">enabled:</dt><dd>{String(data.enabled)}</dd></div>
              <div className="flex gap-2"><dt className="opacity-50 w-28 shrink-0">reserved:</dt><dd>{String(data.reserved)}</dd></div>
              <div className="flex gap-2"><dt className="opacity-50 w-28 shrink-0">status:</dt><dd>{data.status}</dd></div>
              <div className="flex gap-2"><dt className="opacity-50 w-28 shrink-0">activation path:</dt><dd className="leading-relaxed">{data.activation_path}</dd></div>
              <div className="flex gap-2"><dt className="opacity-50 w-28 shrink-0">boundary ref:</dt><dd>{data.boundary_text_ref}</dd></div>
            </dl>
          ) : (
            <p className="opacity-50 text-[10px] animate-pulse">Loading…</p>
          )}
        </div>

        {/* Links */}
        <ul className="space-y-1 text-[10px]">
          <li>
            <a
              href={`${GITHUB_BASE}/MYTHOS_READY.md`}
              target="_blank"
              rel="noopener noreferrer"
              className="underline underline-offset-2 hover:opacity-80 transition-opacity"
              style={{ color: "var(--apohara-lime)" }}
            >
              MYTHOS_READY.md — architectural readiness checklist
            </a>
          </li>
          <li>
            <a
              href={`${GITHUB_BASE}/docs/research/mythos-integration.md`}
              target="_blank"
              rel="noopener noreferrer"
              className="underline underline-offset-2 hover:opacity-80 transition-opacity"
              style={{ color: "var(--apohara-lime)" }}
            >
              docs/research/mythos-integration.md — technical integration design
            </a>
          </li>
        </ul>
      </div>
    </div>
  );
}

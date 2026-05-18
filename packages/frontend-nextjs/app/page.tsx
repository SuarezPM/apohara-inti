// Server Component — renders at build/request time, SEO-friendly.
// PoC Hero migration from packages/frontend/src/sections/Hero.tsx.
// Tailwind classes mirror the SPA tokens defined in tailwind.config.js
// + app/globals.css so we inherit the same look without re-theming.

const REPO_URL = "https://github.com/SuarezPM/apohara-probant";
const PAPER_DOI = "https://doi.org/10.5281/zenodo.20114594";
const SPA_URL = "https://www.apohara.dev";

export default function Home() {
  return (
    <main
      id="top"
      className="relative overflow-hidden border-b border-border/40"
      aria-labelledby="hero-title"
    >
      <div className="container max-w-6xl py-16 lg:py-24 min-h-[calc(100vh-3.5rem)] flex items-center">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-10 lg:gap-12 w-full items-center">
          {/* Left 60% — copy + CTAs */}
          <div className="lg:col-span-3 space-y-8">
            <div className="flex flex-wrap items-center gap-2 font-mono text-[10px] uppercase tracking-widest">
              <span className="inline-flex items-center rounded border border-primary/40 bg-primary/10 px-2 py-0.5 text-primary">
                Apohara PROBANT
              </span>
              <span className="inline-flex items-center rounded border border-border/60 px-2 py-0.5 text-muted-foreground">
                Apache-2.0
              </span>
              <a
                href={PAPER_DOI}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center rounded border border-border/60 px-2 py-0.5 text-muted-foreground hover:text-primary"
              >
                DOI 10.5281/zenodo.20114594
              </a>
              <span className="inline-flex items-center rounded border border-border/60 px-2 py-0.5 text-muted-foreground">
                SSR preview
              </span>
            </div>

            <h1
              id="hero-title"
              className="font-pixel-sans leading-[1.15] tracking-tight text-foreground"
              style={{ fontSize: "clamp(2rem, 5.5vw, 3.5rem)" }}
            >
              A different AI
              <br />
              audits the code{" "}
              <span className="text-primary">your AI</span>
              <br />
              just wrote.
            </h1>

            <p className="text-lg text-muted-foreground leading-relaxed max-w-xl">
              <span className="text-foreground">Apohara PROBANT</span> runs a
              12-vendor adversarial ensemble (9 vendors live in the demo
              droplet today). Each judge runs in an isolated KV-cache
              (Z3-proven{" "}
              <span className="text-foreground">INV-15</span>). Every verdict
              is signed in a SHA-256 chain. No marketing — just measurements.
            </p>

            <div className="flex flex-wrap items-center gap-3 font-pixel-sans text-[11px] tracking-wider">
              <a
                href={SPA_URL}
                className="inline-flex items-center gap-2 rounded-md bg-primary px-5 py-3 text-primary-foreground hover:opacity-90 transition-opacity"
              >
                Try the live demo
                <span aria-hidden="true">→</span>
              </a>
              <a
                href={REPO_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 rounded-md border border-border/60 px-5 py-3 text-foreground hover:text-primary transition-colors"
              >
                View on GitHub
              </a>
            </div>

            <dl className="grid grid-cols-3 gap-6 pt-6 border-t border-border/40 max-w-md">
              <div>
                <dt className="text-xs text-muted-foreground font-mono">
                  Vendors live
                </dt>
                <dd className="text-2xl font-pixel-sans text-primary mt-1">
                  9
                </dd>
              </div>
              <div>
                <dt className="text-xs text-muted-foreground font-mono">
                  JBB block
                </dt>
                <dd className="text-2xl font-pixel-sans text-primary mt-1">
                  93.75<span className="text-sm">%</span>
                </dd>
              </div>
              <div>
                <dt className="text-xs text-muted-foreground font-mono">
                  Hardware
                </dt>
                <dd className="text-2xl font-pixel-sans text-primary mt-1">
                  H100<span className="text-sm">+MI300X</span>
                </dd>
              </div>
            </dl>
          </div>

          {/* Right 40% — shield mark + terminal mockup */}
          <div className="lg:col-span-2 space-y-4">
            <div
              className="aspect-square rounded-md border border-border/30 bg-apohara-dark flex items-center justify-center"
              aria-hidden="true"
            >
              <img
                src="/logo.svg"
                alt="Apohara shield mark"
                width={320}
                height={320}
                className="w-[55%] max-w-[240px]"
              />
            </div>

            <div className="rounded-md border border-border/40 bg-apohara-bg-void overflow-hidden">
              <div className="flex items-center gap-2 px-3 py-1.5 border-b border-border/40 bg-card">
                <span className="text-[10px] font-mono text-muted-foreground">
                  apohara verify
                </span>
                <span className="ml-auto flex gap-1">
                  <span className="h-2 w-2 rounded-full bg-muted-foreground/40" />
                  <span className="h-2 w-2 rounded-full bg-muted-foreground/40" />
                  <span className="h-2 w-2 rounded-full bg-primary/60" />
                </span>
              </div>
              <pre className="px-3 py-4 text-[11px] font-mono leading-relaxed text-muted-foreground whitespace-pre-wrap">
{`> verify "def divide(a,b): return a/b"
[1/3] gemini-3-pro writing review...
[2/3] dispatching adversarial ensemble...
      claude · gpt · deepseek · kimi
      glm · qwen · nemotron · minimax · big-pickle
[3/3] INV-15 isolation enforced`}
                <span className="block text-primary mt-2">
                  verdict: verified
                </span>
              </pre>
            </div>

            <p className="text-[11px] font-mono text-muted-foreground/80 text-center">
              SSR preview — interactive demo lives on{" "}
              <a
                href={SPA_URL}
                className="text-primary hover:underline"
              >
                www.apohara.dev
              </a>
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}

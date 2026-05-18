import { ArrowRight, Github, Terminal } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MythosBadge } from "@/components/MythosBadge";

const REPO_URL = "https://github.com/SuarezPM/apohara-probant";
const PAPER_DOI = "https://doi.org/10.5281/zenodo.20114594";

export function Hero() {
  return (
    <section
      id="top"
      className="relative overflow-hidden border-b border-border/40"
      aria-labelledby="hero-title"
    >
      <div className="container max-w-6xl py-16 lg:py-24 min-h-[calc(100vh-3.5rem)] flex items-center">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-10 lg:gap-12 w-full">
          {/* Left 60% — copy + CTAs */}
          <div className="lg:col-span-3 space-y-8">
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="default" className="font-mono text-[10px] uppercase tracking-widest">
                Stable v1.0
              </Badge>
              <Badge variant="outline" className="font-mono text-[10px]">
                Apache-2.0
              </Badge>
              <Badge variant="outline" className="font-mono text-[10px]">
                <a href={PAPER_DOI} target="_blank" rel="noopener noreferrer" className="hover:text-primary">
                  DOI 10.5281/zenodo.20114594
                </a>
              </Badge>
              <MythosBadge compact />
            </div>

            <h1
              id="hero-title"
              className="font-pixel-sans leading-[1.15] tracking-tight text-foreground"
              style={{ fontSize: "clamp(2rem, 5.5vw, 3.5rem)" }}
            >
              A different AI<br />
              audits the code <span className="text-primary">your AI</span><br />
              just wrote.
            </h1>

            <p className="text-lg text-muted-foreground leading-relaxed max-w-xl">
              12 frontier vendors run adversarial checks in parallel. Each in an
              isolated KV-cache (INV-15). Every verdict signed in a SHA-256
              chain. <span className="text-foreground">No marketing, just measurements.</span>
            </p>

            <div className="flex flex-wrap items-center gap-3">
              <Button asChild size="lg" variant="default" className="font-pixel-sans text-[11px] tracking-wider">
                <a href="#try">
                  Verify my code
                  <ArrowRight className="h-4 w-4" />
                </a>
              </Button>
              <Button asChild size="lg" variant="outline" className="font-pixel-sans text-[11px] tracking-wider">
                <a href={REPO_URL} target="_blank" rel="noopener noreferrer">
                  <Github className="h-4 w-4" />
                  View on GitHub
                </a>
              </Button>
            </div>

            <dl className="grid grid-cols-3 gap-6 pt-6 border-t border-border/40 max-w-md">
              <div>
                <dt className="text-xs text-muted-foreground font-mono">Vendors</dt>
                <dd className="text-2xl font-pixel-sans text-primary mt-1">12</dd>
              </div>
              <div>
                <dt className="text-xs text-muted-foreground font-mono">JBB block</dt>
                <dd className="text-2xl font-pixel-sans text-primary mt-1">93.75<span className="text-sm">%</span></dd>
              </div>
              <div>
                <dt className="text-xs text-muted-foreground font-mono">Hardware</dt>
                <dd className="text-2xl font-pixel-sans text-primary mt-1">H100<span className="text-sm">+MI300X</span></dd>
              </div>
            </dl>
          </div>

          {/* Right 40% — mascot + terminal mockup */}
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
                <Terminal className="h-3 w-3 text-primary" />
                <span className="text-[10px] font-mono text-muted-foreground">apohara verify</span>
                <span className="ml-auto flex gap-1">
                  <span className="h-2 w-2 rounded-full bg-muted-foreground/40" />
                  <span className="h-2 w-2 rounded-full bg-muted-foreground/40" />
                  <span className="h-2 w-2 rounded-full bg-primary/60" />
                </span>
              </div>
              <pre className="px-3 py-4 text-[11px] font-mono leading-relaxed text-muted-foreground">
{`> verify "def divide(a,b): return a/b"
[1/3] gemini-3-pro writing review...
[2/3] dispatching 12 attackers...
      claude · gpt · deepseek · kimi · glm
      qwen · nemotron · minimax · mistral
      grok · perplexity · big-pickle
[3/3] INV-15 isolation enforced
`}
<span className="text-primary">verdict: verified</span><span className="animate-blink text-primary">█</span>
              </pre>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

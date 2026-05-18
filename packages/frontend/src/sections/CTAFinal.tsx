import { ArrowRight, Github } from "lucide-react";
import { Button } from "@/components/ui/button";

const REPO_URL = "https://github.com/SuarezPM/apohara-probant";

export function CTAFinal() {
  return (
    <section className="border-b border-border/40 py-16" aria-labelledby="cta-title">
      <div className="container max-w-4xl text-center">
        <h2
          id="cta-title"
          className="font-pixel-sans text-2xl lg:text-3xl text-foreground leading-tight"
        >
          Verify your code now.
        </h2>
        <p className="mt-3 text-sm text-muted-foreground max-w-lg mx-auto">
          5 free calls/IP/day with the demo key — no signup. Or paste your own
          Gemini key for unlimited runs.
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <Button asChild size="lg" variant="default" className="font-pixel-sans text-[11px] tracking-wider">
            <a href="#try">
              Try the demo
              <ArrowRight className="h-4 w-4" />
            </a>
          </Button>
          <Button asChild size="lg" variant="outline" className="font-pixel-sans text-[11px] tracking-wider">
            <a href={REPO_URL} target="_blank" rel="noopener noreferrer">
              <Github className="h-4 w-4" />
              Star on GitHub
            </a>
          </Button>
        </div>
      </div>
    </section>
  );
}

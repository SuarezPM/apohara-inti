// Server Component — renders at build/request time, SEO-friendly
export default function Home() {
  return (
    <main className="container mx-auto py-16 lg:py-24 min-h-screen flex items-center">
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-12 items-center">
        <div className="lg:col-span-3">
          <p className="font-mono text-[11px] text-primary uppercase tracking-widest mb-3">
            Apache-2.0 · INV-15 enforced · DOI 10.5281/zenodo.20114594
          </p>
          <h1 className="font-pixel-sans text-3xl sm:text-4xl lg:text-5xl leading-tight">
            A different AI audits the code your AI just wrote.
          </h1>
          <p className="mt-6 text-base text-muted-foreground leading-relaxed max-w-xl">
            9 frontier vendors run adversarial checks in parallel. Each in an
            isolated KV-cache (INV-15). Every verdict signed in a SHA-256
            chain. Apache-2.0 OSS. BYOK Gemini key or free demo.
          </p>
        </div>
        <div className="lg:col-span-2">
          <div className="aspect-square rounded-md border border-border/30 bg-apohara-dark flex items-center justify-center">
            {/* logo.svg static-served from /logo.svg */}
            <img
              src="/logo.svg"
              alt="Apohara shield mark"
              width={320}
              height={320}
              className="w-[55%] max-w-[240px]"
            />
          </div>
        </div>
      </div>
    </main>
  );
}

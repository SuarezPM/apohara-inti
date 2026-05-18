const COLS = [
  {
    title: "Products",
    links: [
      { href: "https://github.com/SuarezPM/apohara-probant", label: "Apohara PROBANT" },
      { href: "https://github.com/SuarezPM/Apohara_Context_Forge", label: "Context Forge" },
      { href: "https://github.com/SuarezPM/apohara-aegis", label: "Aegis" },
    ],
  },
  {
    title: "Developers",
    links: [
      { href: "https://github.com/SuarezPM/apohara-probant#readme", label: "Documentation" },
      { href: "https://doi.org/10.5281/zenodo.20114594", label: "Paper (DOI)" },
      { href: "https://api.apohara.dev/health", label: "API status" },
    ],
  },
  {
    title: "Legal",
    links: [
      { href: "https://github.com/SuarezPM/apohara-probant/blob/main/LICENSE", label: "Apache-2.0" },
      { href: "https://github.com/SuarezPM/apohara-probant#privacy", label: "Privacy" },
      { href: "mailto:dimensionequix@gmail.com", label: "Contact" },
    ],
  },
];

export function Footer() {
  return (
    <footer className="py-12 border-t border-border/40" role="contentinfo">
      <div className="container max-w-6xl">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div className="col-span-2 md:col-span-1">
            <a href="#top" className="inline-flex items-center gap-2">
              <img
                src="/logo-bone.svg"
                alt=""
                width={32}
                height={32}
                className="h-8 w-8"
                aria-hidden="true"
              />
              <span className="font-pixel-sans text-xs text-foreground">APOHARA</span>
            </a>
            <p className="mt-3 text-xs text-muted-foreground leading-relaxed max-w-xs">
              Cross-AI code verification with formal memory isolation.
              Apache-2.0. Built by{" "}
              <a
                href="https://github.com/SuarezPM"
                className="text-primary hover:underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                @SuarezPM
              </a>{" "}
              in Argentina.
            </p>
          </div>

          {COLS.map((col) => (
            <div key={col.title}>
              <p className="font-mono text-[10px] text-muted-foreground uppercase tracking-widest mb-3">
                {col.title}
              </p>
              <ul className="space-y-2">
                {col.links.map((link) => (
                  <li key={link.href}>
                    <a
                      href={link.href}
                      target={link.href.startsWith("http") ? "_blank" : undefined}
                      rel={link.href.startsWith("http") ? "noopener noreferrer" : undefined}
                      className="text-sm text-muted-foreground hover:text-primary transition-colors"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-10 pt-6 border-t border-border/40 flex flex-col sm:flex-row items-center justify-between gap-3 text-[11px] font-mono text-muted-foreground">
          <p>&copy; 2026 Apohara &mdash; Apache-2.0 OSS</p>
          <p className="flex items-center gap-3">
            <span>
              Powered by{" "}
              <a
                href="https://github.com/SuarezPM/Apohara_Context_Forge"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                Apohara Context Forge
              </a>
              {" "}&middot; INV-15 enforced
            </span>
            <a
              href="https://apohara-nextjs.vercel.app"
              target="_blank"
              rel="noopener"
              className="text-xs opacity-60 hover:opacity-100 hover:text-primary transition-opacity"
              title="Experimental SSR-rendered Next.js preview"
            >
              Experimental SSR view
            </a>
          </p>
        </div>
      </div>
    </footer>
  );
}

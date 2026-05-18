# Next.js SSR Migration Plan — Apohara PROBANT

## Problem

The current Vite SPA delivers a near-empty `<div id="root">` to crawlers.
Google Search Console shows zero indexed section headings (TrustBar, HowItWorks,
Comparison, WhyThisMatters). Structured data (Schema.org `SoftwareApplication`)
injected via `react-helmet` is not parsed by all crawlers before JS executes.

## SEO Impact Projection

| Metric | Current (CSR SPA) | Post-SSR (Next.js) |
|---|---|---|
| Crawler-visible text on first response | ~0 words | ~400+ words (Hero + TrustBar) |
| Core Web Vitals — LCP | ~2.8s (JS bundle parse) | ~1.2s (HTML streamed) |
| Structured data reliability | ~60% crawlers parse | ~99% crawlers parse |
| Sitelink eligibility | Blocked (no nav in HTML) | Enabled via server-rendered nav |
| Expected organic impression lift | baseline | +40-70% over 3 months |

## Phased Rollout

### Phase 2 Tier 3 (current — this PoC)
- Hero section as Server Component (`app/page.tsx`).
- Edge-runtime API proxy (`app/api/verify/route.ts`) proxies to `api.apohara.dev`.
- Subset font (`PressStart2P-Subset-Apohara.woff2`, 6.6 KB) in `public/fonts/`.
- No production traffic. Dev + build smoke only.

### Phase 2 Follow-up (1 section/week, ~4 weeks)
- Week 1: TrustBar (vendor logos) — static, trivially server-renderable.
- Week 2: HowItWorks + Comparison — static content, no client state.
- Week 3: WhyThisMatters + CTAFinal — static, include Schema.org JSON-LD.
- Week 4: Navbar + Footer — navigation landmarks needed for sitelinks.

Interactive components (TryItPanel, AttackerCard, MatrixRain) remain
Client Components (`"use client"` directive). The architecture splits:
- Static/editorial content → Server Components (crawlable, fast LCP).
- Interactive UI → Client Components (hydrate on client as today).

### Phase 2 End: Cutover
- Vercel project for `packages/frontend-nextjs/` set as new root.
- `packages/frontend/` kept for 30 days behind a redirect.
- No DNS change — same `apohara.dev` domain.

## Risks

| Risk | Mitigation |
|---|---|
| Hydration mismatch on Client Components | Use `suppressHydrationWarning` on dynamic timestamps; render fallback skeletons |
| MatrixRain canvas not SSR-compatible | Already a Client Component — no change needed |
| Edge runtime limits (1 MB bundle, no Node APIs) | API proxy is stateless; no Node APIs used |
| Build time regression (Next 15 full rebuild) | Incremental builds + Turbopack in dev |
| Vercel cold-start (Edge vs Serverless) | All routes use Edge runtime — cold-start ~5ms |

## Timeline

| Milestone | Owner | ETA |
|---|---|---|
| PoC scaffold (this doc) | Pablo / Executor | 2026-05-18 |
| TrustBar + HowItWorks port | Pablo | +1 week |
| Comparison + WhyThisMatters port | Pablo | +2 weeks |
| Navbar + Footer port | Pablo | +3 weeks |
| Vercel cutover + smoke | Pablo | +4 weeks |

## Alternatives Considered

- **Vite SSR plugin** (`vite-plugin-ssr` / Rakkas): avoids framework switch but
  adds complex config; ecosystem smaller than Next.js.
- **Astro**: excellent for static content, but TryItPanel's streaming WebSocket
  would need an Astro Island — similar effort to Next.js without the ecosystem.
- **Prerendering (react-snap / puppeteer)**: crawl-and-snapshot approach; brittle
  on canvas elements (MatrixRain) and doesn't solve dynamic OG images.
- **Decision**: Next.js App Router chosen for ecosystem size, native Edge support,
  and Vercel first-class deployment.

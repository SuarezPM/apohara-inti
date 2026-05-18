# Apohara PROBANT — Next.js SSR PoC

This is a **PoC**, not a production replacement. The Vite frontend at
`packages/frontend/` remains the production deployment.

## Why

The current SPA uses CSR (Client-Side Rendering) — search engines see an
empty `<div id="root">` initially. SSR via Next.js renders content at
request time, so crawlers index full pages. This closes the SEO gap
identified in US-FE-6 without a risky production cutover.

## Status

- Hero section ported as Server Component (`app/page.tsx`).
- Edge-runtime API proxy at `app/api/verify` proxies to api.apohara.dev.
- Build works locally.
- Other sections (TrustBar, TryItPanel, HowItWorks, Comparison,
  WhyThisMatters, CTAFinal, Footer) NOT yet ported.

## Migration plan

Phase 2 Tier 3 (THIS): Hero only.
Phase 2 follow-up: 1 section per week, validate SEO with sitelinks + structured data.
Phase 2 end: cutover via Vercel project-level redirect.

## Run

```bash
cd packages/frontend-nextjs
npm install
npm run build
npm start
```

Dev mode (hot reload, port 3001):

```bash
npm run dev
```

## Out of scope

- Full migration (3-4 weeks per architect estimate).
- Production cutover.
- Vercel project rename / split.

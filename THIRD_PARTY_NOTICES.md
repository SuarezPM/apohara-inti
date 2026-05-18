# Third-Party Notices

Apohara Inti is licensed under Apache-2.0. This file lists the third-party
projects whose patterns or code we adapt, with their original licenses
preserved as required by attribution clauses.

---

## RAPTOR (Recursive Autonomous Penetration Testing and Observation Robot)

- Source: https://github.com/gadievron/raptor
- Authors: Gadi Evron · Daniel Cuthbert · Halvar Flake (Thomas Dullien) ·
  Michael Bargury · John Cartwright · (22 named contributors)
- License: MIT

Patterns adapted in Apohara Inti (2026-05-18):

1. **Prompt envelope with per-call nonce + datamarking**
   - Original: `core/security/prompt_envelope.py`
   - Adapted to: `packages/backend/envelope.py`
   - Reference: Hines et al. (2024), "Defending Against Indirect Prompt
     Injection Attacks With Spotlighting," arXiv 2403.14720.

2. **AST-based audit linter for unsafe f-string interpolation**
   - Original: `core/security/prompt_envelope_audit.py`
   - Adapted to: `packages/backend/scripts/prompt_envelope_audit.py`

3. **NO-HEDGING gate (Stage A→F validation gates, hedge-word list)**
   - Original: `.claude/skills/exploitability-validation/SKILL.md`
   - Adapted to: `packages/backend/judge_gates.py`

The patterns are reimplemented in Python (RAPTOR is a Python project,
but the implementations are independently written to fit Apohara Inti's
FastAPI / Pydantic shapes). Full MIT license text below.

### RAPTOR MIT License

```
MIT License

Copyright (c) 2025 Gadi Evron and contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```

---

## Apohara Guard (sister project, internal)

- Source: internal (`/home/linconx/Apohara-Guard/`, AGPL-3.0)
- Author: Pablo M. Suarez (project lead)
- License: AGPL-3.0

Patterns adapted from Guard's evidence-vault subsystem:

1. **HMAC-signed SHA-256 chain-of-custody**
   - Original: `src/evidence/{vault,chain,crypto}.ts`
   - Adapted to: `packages/backend/verdict_vault.py`

Internal port from the same author (Pablo M. Suarez) — Apache-2.0
relicensing within Apohara Inti is intentional and permitted as the
original author transfers the contribution under Apache-2.0 here.

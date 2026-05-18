"""Judge response quality gates (port of RAPTOR Stage A->F GATES).

The NO-HEDGING gate is the primary hardening: judges that respond with
hedge words ('might', 'maybe', 'possibly') indicate either model uncertainty
or evasion. Either way the operator should see the hedge flagged so they
can re-prompt, downweight, or escalate. Apohara Inti applies this as a
post-process on each adversarial vendor's reply.

Future gates (not yet wired): STRICT_SEQUENCE, PROOF, FULL_COVERAGE,
CONSISTENCY. See RAPTOR `.claude/skills/exploitability-validation/stage-*.md`
for the full taxonomy.
"""
from __future__ import annotations

import re

# RAPTOR hedge-word list, case-insensitive, whitespace-tolerant for multi-word.
# Kept as a public constant so submission/audit copy can reference it.
HEDGE_WORDS: tuple[str, ...] = (
    "might",
    "maybe",
    "possibly",
    "could potentially",
    "may be",
    "uncertain",
    "unclear",
    "perhaps",
    "arguably",
    "seems to",
    "appears to",
    "presumably",
    "likely",
    "i think",
    "i believe",
    "not sure",
    "kind of",
    "sort of",
)


def _compile_pattern() -> re.Pattern[str]:
    parts: list[str] = []
    for word in HEDGE_WORDS:
        escaped = re.escape(word).replace(r"\ ", r"\s+")
        parts.append(rf"\b{escaped}\b")
    return re.compile("|".join(parts), re.IGNORECASE)


_HEDGE_RE = _compile_pattern()


def detect_hedging(text: str) -> tuple[bool, list[str]]:
    """Return ``(has_hedge, matched_words_lowercase_deduplicated)``.

    Empty string returns ``(False, [])``. Whitespace inside multi-word
    hedges is normalized. Order of first appearance is preserved.
    """
    if not text:
        return False, []
    matches = _HEDGE_RE.findall(text)
    normalized = [re.sub(r"\s+", " ", m.lower()) for m in matches]
    seen: set[str] = set()
    unique: list[str] = []
    for m in normalized:
        if m not in seen:
            seen.add(m)
            unique.append(m)
    return bool(unique), unique


def annotate_hedging(reasoning: str) -> str:
    """Prefix ``'[HEDGED:word1,word2] '`` to ``reasoning`` if hedge detected.

    Used by ``main.py`` _run_attackers to surface hedge presence in
    :class:`AttackerReport.reasoning`.
    """
    has_hedge, words = detect_hedging(reasoning)
    if not has_hedge:
        return reasoning
    # `reasoning` is post-processed text returned to the UI/JSON response,
    # NOT sent to another LLM as a prompt. Safe to interpolate.
    return f"[HEDGED:{','.join(words)}] {reasoning}"  # envelope-audit: allow

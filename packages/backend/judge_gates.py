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

# RAPTOR hedge-word list split into two tiers.
#
# HARD_HEDGE  — genuine epistemic hedges that weaken a security verdict.
#               detect_hedging sets has_hard_hedge=True; annotate_hedging
#               prefixes ``[HEDGED:word]``.
# SOFT_HEDGE  — commonly used in decisive security reasoning ("this is
#               likely exploitable" is a conclusion, not a hedge).
#               detect_hedging records them in soft_matches but does NOT
#               set has_hard_hedge; annotate_hedging leaves text unchanged.
#
# HEDGE_WORDS — flat tuple union, kept for backward-compat so any
#               submission/audit copy referencing this name still works.
HARD_HEDGE: tuple[str, ...] = (
    "might",
    "maybe",
    "possibly",
    "could potentially",
    "may be",
    "uncertain",
    "unclear",
    "perhaps",
    "arguably",
    "i think",
    "i believe",
    "not sure",
    "kind of",
    "sort of",
)

SOFT_HEDGE: tuple[str, ...] = (
    "likely",
    "presumably",
    "seems to",
    "appears to",
)

# Preserved for backward-compat: flat union of both tiers.
HEDGE_WORDS: tuple[str, ...] = HARD_HEDGE + SOFT_HEDGE


def _compile_pattern_for(words: tuple[str, ...]) -> re.Pattern[str]:
    parts: list[str] = []
    for word in words:
        escaped = re.escape(word).replace(r"\ ", r"\s+")
        parts.append(rf"\b{escaped}\b")
    return re.compile("|".join(parts), re.IGNORECASE)


_HARD_RE = _compile_pattern_for(HARD_HEDGE)
_SOFT_RE = _compile_pattern_for(SOFT_HEDGE)


def _unique_matches(pattern: re.Pattern[str], text: str) -> list[str]:
    """Return deduplicated, normalized matches for *pattern* in *text*."""
    matches = pattern.findall(text)
    normalized = [re.sub(r"\s+", " ", m.lower()) for m in matches]
    seen: set[str] = set()
    unique: list[str] = []
    for m in normalized:
        if m not in seen:
            seen.add(m)
            unique.append(m)
    return unique


def detect_hedging(text: str) -> tuple[bool, list[str], list[str]]:
    """Return ``(has_hard_hedge, hard_matches, soft_matches)``.

    ``has_hard_hedge`` is True only when at least one HARD_HEDGE word is
    found — SOFT_HEDGE words alone do not raise the flag.

    Empty string returns ``(False, [], [])``. Whitespace inside multi-word
    hedges is normalized. Order of first appearance is preserved.
    """
    if not text:
        return False, [], []
    hard = _unique_matches(_HARD_RE, text)
    soft = _unique_matches(_SOFT_RE, text)
    return bool(hard), hard, soft


def annotate_hedging(reasoning: str) -> str:
    """Prefix ``'[HEDGED:word1,word2] '`` to ``reasoning`` for HARD hedges only.

    If only SOFT matches are present the reasoning is returned unchanged.
    Used by ``main.py`` _run_attackers to surface hedge presence in
    :class:`AttackerReport.reasoning`.
    """
    has_hard, hard_words, _soft = detect_hedging(reasoning)
    if not has_hard:
        return reasoning
    # `reasoning` is post-processed text returned to the UI/JSON response,
    # NOT sent to another LLM as a prompt. Safe to interpolate.
    return f"[HEDGED:{','.join(hard_words)}] {reasoning}"  # envelope-audit: allow

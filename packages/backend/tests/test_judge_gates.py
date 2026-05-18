"""Tests for NO-HEDGING gate."""
from __future__ import annotations

import pytest

from judge_gates import HEDGE_WORDS, annotate_hedging, detect_hedging


def test_clean_text_no_hedge() -> None:
    has, hard, soft = detect_hedging("This code has a SQL injection at line 42.")
    assert has is False
    assert hard == []
    assert soft == []


def test_single_hedge_might() -> None:
    has, hard, soft = detect_hedging("The function might leak memory under load.")
    assert has is True
    assert "might" in hard


def test_multiword_hedge_could_potentially() -> None:
    has, hard, soft = detect_hedging("This could potentially be exploited.")
    assert has is True
    assert "could potentially" in hard


def test_case_insensitive() -> None:
    has, hard, soft = detect_hedging("MAYBE this is a bug.")
    assert has is True
    assert "maybe" in hard


def test_multiple_distinct_hedges_listed() -> None:
    has, hard, soft = detect_hedging("It might be a bug; perhaps the parser is unclear.")
    assert has is True
    assert "might" in hard
    assert "perhaps" in hard
    assert "unclear" in hard


def test_repeated_hedge_deduplicated() -> None:
    has, hard, soft = detect_hedging("It might be a bug. The fix might break things.")
    assert has is True
    assert hard.count("might") == 1


def test_word_boundary_does_not_match_substring() -> None:
    # 'might' inside 'mighty' should not match.
    has, hard, soft = detect_hedging("This mighty function works fine.")
    assert has is False
    assert hard == []


def test_annotate_clean_passthrough() -> None:
    out = annotate_hedging("Definite vuln at line 9.")
    assert out == "Definite vuln at line 9."


def test_annotate_hedge_prefixed() -> None:
    out = annotate_hedging("This might be exploitable.")
    assert out.startswith("[HEDGED:might]")
    assert "This might be exploitable." in out


def test_annotate_multiple_hedges_comma_joined() -> None:
    out = annotate_hedging("It might be a bug; perhaps unclear.")
    assert out.startswith("[HEDGED:")
    prefix = out.split("]")[0]
    assert "might" in prefix
    assert "perhaps" in prefix
    assert "unclear" in prefix


def test_empty_text() -> None:
    has, hard, soft = detect_hedging("")
    assert has is False
    assert hard == []
    assert soft == []


def test_hedge_words_constant_exposed() -> None:
    # Submission text references this list; keep it accessible and complete.
    assert "might" in HEDGE_WORDS
    assert "could potentially" in HEDGE_WORDS
    assert "maybe" in HEDGE_WORDS
    assert len(HEDGE_WORDS) >= 15


def test_likely_is_soft_no_annotation() -> None:
    has, hard, soft = detect_hedging("this is likely exploitable")
    assert has is False
    assert "likely" in soft
    out = annotate_hedging("this is likely exploitable")
    assert out == "this is likely exploitable"


def test_hard_and_soft_combined() -> None:
    has, hard, soft = detect_hedging("might be likely exploitable")
    assert has is True
    assert "might" in hard
    assert "likely" in soft
    out = annotate_hedging("might be likely exploitable")
    assert out.startswith("[HEDGED:might]")
    assert "likely" not in out.split("]")[0]

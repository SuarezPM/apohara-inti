"""Tests for NO-HEDGING gate."""
from __future__ import annotations

import pytest

from judge_gates import HEDGE_WORDS, annotate_hedging, detect_hedging


def test_clean_text_no_hedge() -> None:
    has, words = detect_hedging("This code has a SQL injection at line 42.")
    assert has is False
    assert words == []


def test_single_hedge_might() -> None:
    has, words = detect_hedging("The function might leak memory under load.")
    assert has is True
    assert "might" in words


def test_multiword_hedge_could_potentially() -> None:
    has, words = detect_hedging("This could potentially be exploited.")
    assert has is True
    assert "could potentially" in words


def test_case_insensitive() -> None:
    has, words = detect_hedging("MAYBE this is a bug.")
    assert has is True
    assert "maybe" in words


def test_multiple_distinct_hedges_listed() -> None:
    has, words = detect_hedging("It might be a bug; perhaps the parser is unclear.")
    assert has is True
    assert "might" in words
    assert "perhaps" in words
    assert "unclear" in words


def test_repeated_hedge_deduplicated() -> None:
    has, words = detect_hedging("It might be a bug. The fix might break things.")
    assert has is True
    assert words.count("might") == 1


def test_word_boundary_does_not_match_substring() -> None:
    # 'might' inside 'mighty' should not match.
    has, words = detect_hedging("This mighty function works fine.")
    assert has is False
    assert words == []


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
    has, words = detect_hedging("")
    assert has is False
    assert words == []


def test_hedge_words_constant_exposed() -> None:
    # Submission text references this list; keep it accessible and complete.
    assert "might" in HEDGE_WORDS
    assert "could potentially" in HEDGE_WORDS
    assert "maybe" in HEDGE_WORDS
    assert len(HEDGE_WORDS) >= 15

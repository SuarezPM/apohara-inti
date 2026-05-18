"""Tests for rule_of_two CI gate (US-T1-C-ROT)."""
from __future__ import annotations

import pytest

from rule_of_two import (
    CI_ENV_VARS,
    EXTENDED_CI_ENV_VARS,
    HUMAN_OVERRIDE_ENV,
    RuleOfTwoViolation,
    assert_human_in_loop,
    detect_ci_environment,
    has_human_override,
    has_interactive_tty,
)


# ---------------------------------------------------------------------------
# detect_ci_environment
# ---------------------------------------------------------------------------

def test_detect_ci_environment_no_ci(monkeypatch):
    """Clean environment → no CI detected."""
    for name in EXTENDED_CI_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    assert detect_ci_environment() is None


def test_detect_ci_environment_first_match(monkeypatch):
    """When multiple CI vars set, returns the first one in the list."""
    for name in EXTENDED_CI_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    # Set two vars; expect the one that appears earlier in the tuple.
    first = EXTENDED_CI_ENV_VARS[0]   # "CI"
    second = EXTENDED_CI_ENV_VARS[1]  # "GITHUB_ACTIONS"
    monkeypatch.setenv(first, "true")
    monkeypatch.setenv(second, "true")
    assert detect_ci_environment() == first


def test_detect_ci_environment_single(monkeypatch):
    """Detects a single set CI var."""
    for name in EXTENDED_CI_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("CIRCLECI", "1")
    assert detect_ci_environment() == "CIRCLECI"


# ---------------------------------------------------------------------------
# has_human_override
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("val", ["1", "true", "yes", "on", "TRUE", "YES", "ON"])
def test_override_truthy_values(monkeypatch, val):
    """Truthy override values are accepted."""
    monkeypatch.setenv(HUMAN_OVERRIDE_ENV, val)
    assert has_human_override() is True


@pytest.mark.parametrize("val", ["0", "false", "no", "off", "", "maybe"])
def test_override_falsy_values(monkeypatch, val):
    """Non-truthy override values are rejected."""
    monkeypatch.setenv(HUMAN_OVERRIDE_ENV, val)
    assert has_human_override() is False


def test_override_absent(monkeypatch):
    """Missing env var → no override."""
    monkeypatch.delenv(HUMAN_OVERRIDE_ENV, raising=False)
    assert has_human_override() is False


# ---------------------------------------------------------------------------
# assert_human_in_loop — allow paths
# ---------------------------------------------------------------------------

def test_no_ci_no_tty_allows(monkeypatch):
    """Local dev (no CI, no TTY, no override) is allowed — no CI detected."""
    for name in EXTENDED_CI_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.delenv(HUMAN_OVERRIDE_ENV, raising=False)
    # Should not raise; not in CI.
    assert_human_in_loop("deploy")


def test_ci_with_tty_allows(monkeypatch):
    """Interactive CI session (CI + TTY) is allowed."""
    for name in EXTENDED_CI_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("CI", "true")
    monkeypatch.delenv(HUMAN_OVERRIDE_ENV, raising=False)
    # Patch has_interactive_tty to return True (simulates interactive CI).
    monkeypatch.setattr("rule_of_two.has_interactive_tty", lambda: True)
    assert_human_in_loop("deploy")


def test_ci_no_tty_with_override_allows(monkeypatch):
    """CI + no TTY + override → allowed."""
    for name in EXTENDED_CI_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv(HUMAN_OVERRIDE_ENV, "1")
    monkeypatch.setattr("rule_of_two.has_interactive_tty", lambda: False)
    assert_human_in_loop("auto-merge")


# ---------------------------------------------------------------------------
# assert_human_in_loop — block path
# ---------------------------------------------------------------------------

def test_ci_no_tty_no_override_blocks(monkeypatch):
    """Canonical block: CI + no TTY + no override raises RuleOfTwoViolation."""
    for name in EXTENDED_CI_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("CI", "true")
    monkeypatch.delenv(HUMAN_OVERRIDE_ENV, raising=False)
    monkeypatch.setattr("rule_of_two.has_interactive_tty", lambda: False)

    with pytest.raises(RuleOfTwoViolation):
        assert_human_in_loop("auto-push")


def test_action_name_in_error(monkeypatch):
    """Error message contains the action string."""
    for name in EXTENDED_CI_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("BUILDKITE", "1")
    monkeypatch.delenv(HUMAN_OVERRIDE_ENV, raising=False)
    monkeypatch.setattr("rule_of_two.has_interactive_tty", lambda: False)

    with pytest.raises(RuleOfTwoViolation, match="auto-deploy"):
        assert_human_in_loop("auto-deploy")


# ---------------------------------------------------------------------------
# Custom env var list
# ---------------------------------------------------------------------------

def test_custom_env_vars_list(monkeypatch):
    """Caller can pass own CI marker list (e.g., internal CI markers)."""
    monkeypatch.delenv("MY_INTERNAL_CI", raising=False)
    for name in EXTENDED_CI_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.delenv(HUMAN_OVERRIDE_ENV, raising=False)
    monkeypatch.setattr("rule_of_two.has_interactive_tty", lambda: False)

    custom_vars = ("MY_INTERNAL_CI",)
    # Without the var set → no CI detected → allowed.
    assert_human_in_loop("deploy", env_vars=custom_vars)

    # Now set the internal CI var → should block.
    monkeypatch.setenv("MY_INTERNAL_CI", "1")
    with pytest.raises(RuleOfTwoViolation):
        assert_human_in_loop("deploy", env_vars=custom_vars)


def test_detect_ci_environment_custom_list(monkeypatch):
    """detect_ci_environment respects a custom env_vars list."""
    for name in EXTENDED_CI_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("MY_CI", "yes")
    result = detect_ci_environment(env_vars=("MY_CI", "OTHER_CI"))
    assert result == "MY_CI"

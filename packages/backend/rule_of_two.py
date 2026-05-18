"""Rule-of-Two CI gate (port from gadievron/raptor MIT).

Meta's "Agents Rule of Two" pattern: of (A) detectable CI environment,
(B) interactive TTY, (C) explicit human authorization, require at least 2
to allow a destructive agentic action. We invert the question: BLOCK the
action if the agent is running in CI without TTY and without explicit
human override. Used to prevent unattended agents from running
auto-merge/auto-push/auto-deploy without human review.
"""
from __future__ import annotations

import os
import sys
from typing import Iterable

# 16 CI env var names (canonical set per RAPTOR + popular CI providers).
CI_ENV_VARS: tuple[str, ...] = (
    "CI", "GITHUB_ACTIONS", "JENKINS_URL", "TF_BUILD", "BUILDKITE",
    "DRONE", "CIRRUS_CI", "WOODPECKER", "GITLAB_CI", "BAMBOO_BUILDKEY",
    "TRAVIS", "APPVEYOR", "CIRCLECI", "TEAMCITY_VERSION",
    "AZURE_HTTP_USER_AGENT", "NETLIFY",
)

# Vercel uses NEXT_PUBLIC_VERCEL_URL or VERCEL (distinct from local dev).
EXTENDED_CI_ENV_VARS: tuple[str, ...] = CI_ENV_VARS + ("VERCEL",)

# Explicit human authorization override (must be set INTENTIONALLY).
HUMAN_OVERRIDE_ENV = "APOHARA_WRITE_AGENT_TRUST"


class RuleOfTwoViolation(PermissionError):
    """Raised when destructive action attempted without sufficient quorum."""


def detect_ci_environment(env_vars: Iterable[str] = EXTENDED_CI_ENV_VARS) -> str | None:
    """Return the first set CI env var name, or None if no CI detected."""
    for name in env_vars:
        if os.environ.get(name):
            return name
    return None


def has_interactive_tty() -> bool:
    """True if stdin AND stdout are both TTYs (interactive shell)."""
    try:
        return sys.stdin.isatty() and sys.stdout.isatty()
    except (OSError, AttributeError):
        return False


def has_human_override(override_env: str = HUMAN_OVERRIDE_ENV) -> bool:
    """True if the explicit human-trust env var is set to a truthy value."""
    val = os.environ.get(override_env, "").strip().lower()
    return val in ("1", "true", "yes", "on")


def assert_human_in_loop(
    action: str,
    *,
    env_vars: Iterable[str] = EXTENDED_CI_ENV_VARS,
    override_env: str = HUMAN_OVERRIDE_ENV,
) -> None:
    """Block ``action`` when running in CI without TTY and without override.

    Apply rule-of-two: of (ci_detected, has_tty, has_override), require >=2
    of these signals NOT-pointing-to-CI to allow. Concretely:
      - If CI detected AND no TTY AND no override -> BLOCK
      - Else allow (e.g., CI + TTY = interactive CI session OK; CI + override
        = explicit human trust OK; not-CI = local dev OK).

    Raises:
        RuleOfTwoViolation: with descriptive message if action is blocked.
    """
    ci_var = detect_ci_environment(env_vars)
    tty_ok = has_interactive_tty()
    override_ok = has_human_override(override_env)

    if ci_var and not tty_ok and not override_ok:
        raise RuleOfTwoViolation(
            f"Action {action!r} blocked: running in CI ({ci_var}) without "
            f"TTY and without {override_env}=1 override. Set "
            f"{override_env}=1 (with explicit human review) to authorize "
            f"this action in unattended environments."
        )

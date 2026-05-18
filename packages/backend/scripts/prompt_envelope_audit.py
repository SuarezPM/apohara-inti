#!/usr/bin/env python3
"""AST-based linter flagging unsafe f-string interpolation of untrusted attrs.

Port of RAPTOR ``core/security/prompt_envelope_audit.py``.

Walks .py files in the given directory. For each f-string node
(``ast.FormattedValue``), checks whether the formatted expression is a
``Name`` or ``Attribute`` resolving to one of :data:`UNTRUSTED_ATTRS`. If
so, reports a violation unless the line carries the ``# envelope-audit:
allow`` suffix.

CLI::

    python scripts/prompt_envelope_audit.py packages/backend/

Exits 0 if clean, 1 if any violation found (diagnostics on stderr), 2 on
usage error. Used as a pre-commit hook or CI gate. The companion module
``envelope.py`` provides the safe path; this audit ensures developers
route through it instead of raw f-strings.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

UNTRUSTED_ATTRS: frozenset[str] = frozenset(
    {
        "task_input",
        "gemini_output",
        "user_code",
        "code",
        "reasoning",
        "vulnerable_code",
        "message",
        "description",
        "prompt_text",
        "attacker_output",
    }
)

ALLOW_MARKER = "# envelope-audit: allow"


class Violation:
    __slots__ = ("path", "lineno", "col", "name")

    def __init__(self, path: Path, lineno: int, col: int, name: str) -> None:
        self.path = path
        self.lineno = lineno
        self.col = col
        self.name = name

    def __str__(self) -> str:
        return (
            f"{self.path}:{self.lineno}:{self.col}: "
            f"untrusted attr '{self.name}' interpolated into f-string"
        )


def _expr_name(expr: ast.expr) -> str | None:
    """Return bare name or final ``.attr`` if expression resolves to one."""
    if isinstance(expr, ast.Name):
        return expr.id
    if isinstance(expr, ast.Attribute):
        return expr.attr
    return None


def _line_allowed(source_lines: list[str], lineno: int) -> bool:
    if 1 <= lineno <= len(source_lines):
        return ALLOW_MARKER in source_lines[lineno - 1]
    return False


def audit_source(path: Path, source: str) -> list[Violation]:
    """Return all violations in ``source``. Empty list = clean."""
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []
    source_lines = source.splitlines()
    violations: list[Violation] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.JoinedStr):
            continue
        for child in node.values:
            if not isinstance(child, ast.FormattedValue):
                continue
            name = _expr_name(child.value)
            if name and name in UNTRUSTED_ATTRS:
                if _line_allowed(source_lines, child.lineno):
                    continue
                violations.append(
                    Violation(
                        path=path,
                        lineno=child.lineno,
                        col=child.col_offset,
                        name=name,
                    )
                )
    return violations


def audit_path(root: Path) -> list[Violation]:
    """Recursively audit all ``.py`` files under ``root``."""
    all_violations: list[Violation] = []
    for py in root.rglob("*.py"):
        try:
            rel = py.relative_to(root)
        except ValueError:
            rel = py
        parts = set(rel.parts)
        if ".venv" in parts or "node_modules" in parts or "__pycache__" in parts:
            continue
        # Skip the auditor itself: its UNTRUSTED_ATTRS literals would self-flag.
        if py.name == "prompt_envelope_audit.py":
            continue
        try:
            source = py.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        all_violations.extend(audit_source(py, source))
    return all_violations


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: prompt_envelope_audit.py <path> [<path>...]", file=sys.stderr)
        return 2
    all_violations: list[Violation] = []
    for arg in argv[1:]:
        path = Path(arg)
        if not path.exists():
            print(f"warning: {path} does not exist", file=sys.stderr)
            continue
        if path.is_file():
            all_violations.extend(audit_source(path, path.read_text(encoding="utf-8")))
        else:
            all_violations.extend(audit_path(path))
    for v in all_violations:
        print(str(v), file=sys.stderr)
    if all_violations:
        print(f"\n{len(all_violations)} violation(s) found.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

"""Tests for prompt_envelope_audit AST linter."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parent.parent / "scripts" / "prompt_envelope_audit.py"
)


def _run(*args: str) -> tuple[int, str, str]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


def test_clean_file_returns_zero(tmp_path: Path) -> None:
    f = tmp_path / "clean.py"
    f.write_text('x = 1\ny = f"value is {x}"\n')
    rc, _, err = _run(str(f))
    assert rc == 0, f"Expected clean exit, stderr: {err}"


def test_unsafe_task_input_flagged(tmp_path: Path) -> None:
    f = tmp_path / "unsafe.py"
    f.write_text(
        "def build(task_input):\n"
        '    return f"Audit: {task_input}"\n'
    )
    rc, _, err = _run(str(f))
    assert rc == 1
    assert "untrusted attr 'task_input'" in err
    assert "unsafe.py:2" in err


def test_unsafe_attribute_form_flagged(tmp_path: Path) -> None:
    f = tmp_path / "attr.py"
    f.write_text(
        "def build(req):\n"
        '    return f"Audit: {req.task_input}"\n'
    )
    rc, _, err = _run(str(f))
    assert rc == 1
    assert "untrusted attr 'task_input'" in err


def test_allow_marker_skips_line(tmp_path: Path) -> None:
    f = tmp_path / "allowed.py"
    f.write_text(
        "def build(task_input):\n"
        '    return f"Audit: {task_input}"  # envelope-audit: allow\n'
    )
    rc, _, _ = _run(str(f))
    assert rc == 0


def test_no_args_returns_usage_error() -> None:
    rc, _, err = _run()
    assert rc == 2
    assert "Usage" in err


def test_directory_recursive(tmp_path: Path) -> None:
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "bad.py").write_text(
        "def f(task_input):\n    return f'{task_input}'\n"
    )
    (sub / "ok.py").write_text("x = 1\n")
    rc, _, err = _run(str(tmp_path))
    assert rc == 1
    assert "bad.py" in err


def test_envelope_helper_call_not_flagged(tmp_path: Path) -> None:
    """build_envelope() with task_input as dict VALUE is the safe path."""
    f = tmp_path / "safe.py"
    f.write_text(
        "from envelope import build_envelope\n"
        "def build(task_input):\n"
        '    return build_envelope("inst", {"x": task_input})\n'
    )
    rc, _, _ = _run(str(f))
    # Function call argument is NOT an f-string interpolation, so clean.
    assert rc == 0


def test_skip_venv_and_pycache(tmp_path: Path) -> None:
    venv = tmp_path / ".venv" / "lib"
    venv.mkdir(parents=True)
    (venv / "bad.py").write_text(
        "def f(task_input):\n    return f'{task_input}'\n"
    )
    rc, _, _ = _run(str(tmp_path))
    assert rc == 0


def test_subscript_string_constant_flagged(tmp_path: Path) -> None:
    f = tmp_path / "subscript_bad.py"
    f.write_text(
        "def build(data):\n"
        "    return f\"Audit: {data['task_input']}\"\n"
    )
    rc, _, err = _run(str(f))
    assert rc == 1
    assert "untrusted attr 'task_input'" in err
    assert "subscript_bad.py:2" in err


def test_subscript_variable_index_not_flagged(tmp_path: Path) -> None:
    f = tmp_path / "subscript_var.py"
    f.write_text(
        "def build(data, key):\n"
        '    return f"Value: {data[key]}"\n'
    )
    rc, _, _ = _run(str(f))
    assert rc == 0


def test_subscript_non_untrusted_key_not_flagged(tmp_path: Path) -> None:
    f = tmp_path / "subscript_safe.py"
    f.write_text(
        "def build(data):\n"
        "    return f\"Value: {data['safe_key']}\"\n"
    )
    rc, _, _ = _run(str(f))
    assert rc == 0

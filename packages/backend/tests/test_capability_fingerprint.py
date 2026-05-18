"""Tests for capability fingerprinting (US-T2-C-CAP-FP, port from RAPTOR PR #545)."""
from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

import pytest

from capability_fingerprint import (
    CAPABILITY_BUCKETS,
    CapabilityFingerprint,
    append_to_store,
    classify_code,
    detect_drift,
)


# ---------------------------------------------------------------------------
# classify_code — exec detection
# ---------------------------------------------------------------------------

def test_classify_exec_eval():
    """eval() call → exec bucket set."""
    fp = classify_code("result = eval(user_input)")
    assert fp.exec is True


def test_classify_exec_subprocess():
    """subprocess.run → exec bucket set."""
    fp = classify_code('subprocess.run(["ls", "-la"])')
    assert fp.exec is True


def test_classify_exec_os_system():
    """os.system → exec bucket set."""
    fp = classify_code('import os; os.system("whoami")')
    assert fp.exec is True


# ---------------------------------------------------------------------------
# classify_code — network detection
# ---------------------------------------------------------------------------

def test_classify_network_requests():
    """requests. prefix → network bucket set."""
    fp = classify_code("resp = requests.get('https://example.com')")
    assert fp.network is True


def test_classify_network_fetch():
    """fetch( call → network bucket set."""
    fp = classify_code("const data = await fetch('https://api.example.com/data')")
    assert fp.network is True


# ---------------------------------------------------------------------------
# classify_code — parser detection
# ---------------------------------------------------------------------------

def test_classify_parser_json_loads():
    """json.loads → parser bucket set."""
    fp = classify_code("data = json.loads(raw_body)")
    assert fp.parser is True


def test_classify_parser_yaml_load():
    """yaml.load → parser bucket set (unsafe variant)."""
    fp = classify_code("cfg = yaml.load(stream)")
    assert fp.parser is True


def test_classify_parser_json_parse_js():
    """JSON.parse (JS) → parser bucket set."""
    fp = classify_code("const obj = JSON.parse(response.body);")
    assert fp.parser is True


# ---------------------------------------------------------------------------
# classify_code — format_string detection
# ---------------------------------------------------------------------------

def test_classify_format_string_printf():
    """printf with %s → format_string bucket set."""
    fp = classify_code('printf("%s", user_data);')
    assert fp.format_string is True


# ---------------------------------------------------------------------------
# classify_code — sha256 correctness
# ---------------------------------------------------------------------------

def test_classify_sha256_correct():
    """sha256 field equals hashlib digest of the same text."""
    text = "x = 1 + 2"
    fp = classify_code(text)
    expected = hashlib.sha256(text.encode("utf-8")).hexdigest()
    assert fp.sha256 == expected


def test_classify_sha256_empty():
    """Empty text → sha256 of empty string, all buckets False."""
    fp = classify_code("")
    expected = hashlib.sha256(b"").hexdigest()
    assert fp.sha256 == expected
    for bucket in CAPABILITY_BUCKETS:
        assert getattr(fp, bucket) is False, f"bucket {bucket!r} should be False for empty input"


# ---------------------------------------------------------------------------
# classify_code — clean code yields all-False
# ---------------------------------------------------------------------------

def test_classify_clean_code_all_false():
    """Pure arithmetic code raises no capability flags."""
    fp = classify_code("def add(a, b):\n    return a + b\n")
    for bucket in CAPABILITY_BUCKETS:
        assert getattr(fp, bucket) is False, f"bucket {bucket!r} should be False for clean code"


# ---------------------------------------------------------------------------
# append_to_store + read back
# ---------------------------------------------------------------------------

def test_append_and_read_back():
    """Appended fingerprint can be read back and matches original."""
    fp = classify_code("import subprocess\nsubprocess.run(['ls'])")
    with tempfile.TemporaryDirectory() as tmpdir:
        store = Path(tmpdir) / "sub" / "store.jsonl"
        append_to_store(fp, store)
        lines = store.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 1
        recovered = json.loads(lines[0])
        assert recovered["sha256"] == fp.sha256
        assert recovered["exec"] is True


def test_append_multiple_entries():
    """Multiple appends produce multiple JSONL lines."""
    fp1 = classify_code("eval('1+1')")
    fp2 = classify_code("x = 42")
    with tempfile.TemporaryDirectory() as tmpdir:
        store = Path(tmpdir) / "store.jsonl"
        append_to_store(fp1, store)
        append_to_store(fp2, store)
        lines = store.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 2


# ---------------------------------------------------------------------------
# detect_drift
# ---------------------------------------------------------------------------

def test_detect_drift_added():
    """New capability in cur → appears in added list."""
    prev = classify_code("x = 1")
    cur = classify_code("eval('x')")
    drift = detect_drift(prev, cur)
    assert "exec" in drift["added"]
    assert drift["removed"] == []


def test_detect_drift_removed():
    """Capability present in prev but absent in cur → appears in removed list."""
    prev = classify_code("eval('x')")
    cur = classify_code("x = 1")
    drift = detect_drift(prev, cur)
    assert "exec" in drift["removed"]
    assert drift["added"] == []


def test_detect_drift_no_change():
    """Identical fingerprints → empty added and removed."""
    fp = classify_code("import json\njson.loads(raw)")
    drift = detect_drift(fp, fp)
    assert drift == {"added": [], "removed": []}


def test_detect_drift_both_directions():
    """Added and removed can both be non-empty simultaneously."""
    prev = classify_code("eval('x')")             # exec=True, network=False
    cur = classify_code("requests.get('http://x')") # exec=False, network=True
    drift = detect_drift(prev, cur)
    assert "network" in drift["added"]
    assert "exec" in drift["removed"]

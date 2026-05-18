"""Capability fingerprinting for code prompts (port from gadievron/raptor PR #545).

Classifies code snippets into 10 capability buckets via lightweight AST + regex
heuristics. SHA-256-keyed persistent store lets us detect capability drift
across versions (`detect_drift(prev, cur)`).

Use case in Apohara PROBANT: tag every code prompt sent to /v1/verify with its
capability fingerprint, so we can route high-risk prompts (e.g. `exec` +
`network`) to a more aggressive verification policy.
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

CAPABILITY_BUCKETS = (
    "alloc",           # malloc/calloc/new/Buffer.allocUnsafe
    "exec",            # exec/eval/subprocess/system
    "network",         # http/socket/fetch/requests/curl
    "string_overflow", # strcpy/sprintf/gets unsafe C patterns
    "scan",            # scandir/glob/os.walk
    "memory_copy",     # memcpy/memmove/bcopy
    "format_string",   # printf %s with user input
    "parser",          # json.loads, yaml.load, xml parsing
    "integer_parse",   # int(), parseInt, atoi, parseInteger
    "toctou",          # time-of-check-time-of-use race patterns (stat then open)
)


@dataclass
class CapabilityFingerprint:
    sha256: str
    alloc: bool = False
    exec: bool = False
    network: bool = False
    string_overflow: bool = False
    scan: bool = False
    memory_copy: bool = False
    format_string: bool = False
    parser: bool = False
    integer_parse: bool = False
    toctou: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# Regex patterns — fast first-pass; AST tightens for Python prompts.
_PATTERNS = {
    "exec": re.compile(
        r"\b(exec|eval|os\.system|subprocess\.(run|call|Popen|check_output)|shell_exec|child_process\.exec)\b"
    ),
    "network": re.compile(
        r"\b(socket\.|urllib|requests\.|httpx\.|axios\.|XMLHttpRequest|http\.)\b|(?<!\w)fetch\s*\(|(?<!\w)(curl|wget)\s+"
    ),
    "alloc": re.compile(
        r"\b(malloc|calloc|realloc|alloca|new\s+\w+|Buffer\.allocUnsafe)\b"
    ),
    "string_overflow": re.compile(
        r"\b(strcpy|strcat|sprintf|gets|scanf)\s*\("
    ),
    "scan": re.compile(
        r"\b(os\.walk|os\.scandir|glob\.glob|fs\.readdir|opendir|scandir)\b"
    ),
    "memory_copy": re.compile(
        r"\b(memcpy|memmove|bcopy)\s*\("
    ),
    "format_string": re.compile(
        r'\b(printf|sprintf|fprintf)\s*\([^)]*%[sxd]'
    ),
    "parser": re.compile(
        r"\b(json\.loads|yaml\.(safe_)?load|xml\.etree|xmltodict\.parse|csv\.reader|JSON\.parse)\b"
    ),
    "integer_parse": re.compile(
        r"\b(int\(|parseInt\(|atoi\(|Integer\.parseInt|strtol\()"
    ),
    "toctou": re.compile(
        r"\b(os\.stat|os\.path\.exists|fs\.exists).*\n.*\b(open|fs\.open|fopen)\b",
        re.DOTALL,
    ),
}


def classify_code(text: str) -> CapabilityFingerprint:
    """Classify capabilities present in a code snippet via regex + best-effort AST."""
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    flags: dict[str, bool] = {b: False for b in CAPABILITY_BUCKETS}
    for cap, pattern in _PATTERNS.items():
        if pattern.search(text):
            flags[cap] = True
    # AST tighten for Python — catches things regex misses (e.g. eval as
    # method call eval=func; eval(x)).
    try:
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                fn = node.func
                name = fn.id if isinstance(fn, ast.Name) else (
                    fn.attr if isinstance(fn, ast.Attribute) else ""
                )
                if name in ("eval", "exec", "compile"):
                    flags["exec"] = True
                if name in ("loads", "load") and isinstance(fn, ast.Attribute):
                    flags["parser"] = True
    except SyntaxError:
        pass  # not valid Python; regex pass already covered
    return CapabilityFingerprint(sha256=sha, **flags)


def append_to_store(fp: CapabilityFingerprint, store_path: Path) -> None:
    """Append fingerprint to JSONL store."""
    store_path.parent.mkdir(parents=True, exist_ok=True)
    with store_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(fp.to_dict()) + "\n")


def detect_drift(
    prev: CapabilityFingerprint, cur: CapabilityFingerprint
) -> dict[str, list[str]]:
    """Return {added: [...], removed: [...]} capability lists."""
    added = [b for b in CAPABILITY_BUCKETS if getattr(cur, b) and not getattr(prev, b)]
    removed = [b for b in CAPABILITY_BUCKETS if getattr(prev, b) and not getattr(cur, b)]
    return {"added": added, "removed": removed}

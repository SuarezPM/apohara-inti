"""Apohara PROBANT MCP server — exposes verify/audit/list tools.

Run: python -m mcp_server
Or:  python packages/backend/mcp_server.py

Wire protocol: stdio (MCP standard). Compatible with Claude Desktop,
Claude Code, Cursor, Zed.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from typing import Any

# `mcp` library may not be installed locally; gate import.
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

import httpx

DEFAULT_API_BASE = os.environ.get("APOHARA_PROBANT_API", "https://api.apohara.dev")


async def call_verify(api_base: str, code: str, gemini_key: str | None) -> dict[str, Any]:
    """POST /v1/verify or /v1/demo_verify depending on key presence."""
    endpoint = "/v1/verify" if gemini_key else "/v1/demo_verify"
    body: dict[str, Any] = {"task_input": code}
    if gemini_key:
        body["gemini_api_key"] = gemini_key
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(f"{api_base.rstrip('/')}{endpoint}", json=body)
        resp.raise_for_status()
        return resp.json()  # type: ignore[no-any-return]


async def call_audit(api_base: str, verdict_id: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{api_base.rstrip('/')}/v1/audit/{verdict_id}")
        resp.raise_for_status()
        return resp.json()  # type: ignore[no-any-return]


async def call_recent(api_base: str, limit: int, admin_key: str) -> dict[str, Any]:
    params: dict[str, Any] = {"limit": limit}
    if admin_key:
        params["admin_key"] = admin_key
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            f"{api_base.rstrip('/')}/v1/audit/recent",
            params=params,
        )
        resp.raise_for_status()
        return resp.json()  # type: ignore[no-any-return]


def build_server() -> "Server":
    """Construct MCP server with 3 tools."""
    if not MCP_AVAILABLE:
        raise RuntimeError("`mcp` library not installed. Run: pip install mcp")

    server = Server("apohara-probant-mcp")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="verify_code",
                description=(
                    "Verify AI-generated code with the 9-vendor adversarial ensemble. "
                    "Returns verdict (verified/risky/blocked), per-attacker reasoning, "
                    "and a signed_hash for audit lookup."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Code or task to verify",
                        },
                        "gemini_api_key": {
                            "type": "string",
                            "description": (
                                "Optional BYOK Gemini key. If absent, uses shared "
                                "demo quota (5 requests/IP/day)."
                            ),
                        },
                    },
                    "required": ["code"],
                },
            ),
            Tool(
                name="get_audit",
                description=(
                    "Fetch a previously signed verdict from the SHA-256 + HMAC ledger."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "verdict_id": {
                            "type": "string",
                            "description": "signed_hash from a prior verify call",
                        }
                    },
                    "required": ["verdict_id"],
                },
            ),
            Tool(
                name="list_recent_verdicts",
                description=(
                    "List the most recent N audit ledger entries. "
                    "Requires APOHARA_ADMIN_KEY env var on the backend."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "default": 20}
                    },
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        api_base = os.environ.get("APOHARA_PROBANT_API", DEFAULT_API_BASE)
        admin_key = os.environ.get("APOHARA_ADMIN_KEY", "").strip()
        try:
            if name == "verify_code":
                result = await call_verify(
                    api_base,
                    arguments["code"],
                    arguments.get("gemini_api_key"),
                )
            elif name == "get_audit":
                result = await call_audit(api_base, arguments["verdict_id"])
            elif name == "list_recent_verdicts":
                limit = int(arguments.get("limit", 20))
                result = await call_recent(api_base, limit, admin_key)
            else:
                result = {"error": f"unknown tool: {name}"}
        except httpx.HTTPStatusError as exc:
            result = {"error": f"HTTP {exc.response.status_code}: {exc.response.text[:200]}"}
        except httpx.HTTPError as exc:
            result = {"error": f"network error: {exc!s}"}
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    return server


async def main() -> None:
    if not MCP_AVAILABLE:
        print(
            "ERROR: `mcp` library not installed. Run: pip install mcp",
            file=sys.stderr,
        )
        sys.exit(1)
    server = build_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())

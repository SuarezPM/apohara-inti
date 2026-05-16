"""VeeaONE control plane stub — US-009 mock for local development.

This mock simulates the Veea TerraFabric control plane responses for three
endpoints used by Apohara Inti integration tests. It is not a faithful
implementation of TerraFabric; it returns canned JSON for /healthz, /devices,
and /policies so the docker-compose smoke run can verify wiring without
hitting Veea's production API.

Production deployments would replace this with the real TerraFabric control
plane via Veea's API. See ../terrafabric-stack.md for the integration pattern.
"""
from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="VeeaONE Stub", version="0.1.0")


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok", "vendor": "veea-stub", "control_plane": "terrafabric-mock"}


@app.get("/devices")
def devices() -> dict:
    return {
        "devices": [
            {"id": "mock-edge-01", "status": "online", "site": "apohara-inti-dev"},
        ]
    }


@app.get("/policies")
def policies() -> dict:
    return {
        "policies": [
            {"id": "default", "enforced": True, "linked_proxy": "lobstertrap-default"},
        ]
    }

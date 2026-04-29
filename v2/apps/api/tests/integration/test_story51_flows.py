"""Story 5.1: CRUD drafts + validate (tenant RLS quando DB disponivel)."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

TENANT = "11111111-1111-4111-8111-111111111111"
_HDR = {"X-Dev-Tenant-Id": TENANT, "X-Dev-Roles": "operator"}

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL") or not os.getenv("ALEMBIC_SYNC_URL"),
    reason="needs DATABASE_URL and ALEMBIC_SYNC_URL (CI postgres)",
)


def _minimal_valid() -> dict:
    return {
        "nodes": [
            {"id": "t_atdd", "kind": "trigger"},
            {"id": "a_atdd", "kind": "action"},
        ],
        "edges": [{"source": "t_atdd", "target": "a_atdd"}],
    }


@pytest.mark.integration
def test_flow_create_invalid_definition_422(client: TestClient) -> None:
    r = client.post(
        "/v1/me/flows",
        headers=_HDR,
        json={"name": "bad-draft", "definition": {"nodes": [], "edges": []}},
    )
    assert r.status_code == 422, r.text
    body = r.json()
    assert body.get("code") == "validation_error"
    assert isinstance(body.get("errors"), list)


@pytest.mark.integration
def test_flow_patch_cycle_rejected_422(client: TestClient) -> None:
    r = client.post(
        "/v1/me/flows",
        headers=_HDR,
        json={"name": "patch-cycle", "definition": _minimal_valid()},
    )
    assert r.status_code == 201, r.text
    fid = r.json()["id"]
    cyclic = {
        "nodes": [
            {"id": "t1", "kind": "trigger"},
            {"id": "c1", "kind": "condition"},
            {"id": "a1", "kind": "action"},
        ],
        "edges": [
            {"source": "t1", "target": "c1"},
            {"source": "c1", "target": "a1"},
            {"source": "a1", "target": "c1"},
        ],
    }
    r2 = client.patch(
        f"/v1/me/flows/{fid}",
        headers=_HDR,
        json={"definition": cyclic},
    )
    assert r2.status_code == 422, r2.text

    r3 = client.get(f"/v1/me/flows/{fid}", headers=_HDR)
    assert r3.status_code == 200, r3.text
    assert r3.json()["valid"] is True
    assert r3.json()["definition"] == _minimal_valid()


@pytest.mark.integration
def test_flow_create_and_list(client: TestClient) -> None:
    name = "atdd-draft-51-list"
    r = client.post(
        "/v1/me/flows",
        headers=_HDR,
        json={"name": name, "definition": _minimal_valid()},
    )
    assert r.status_code == 201, r.text
    data = r.json()
    fid = data["id"]
    assert data["valid"] is True

    r2 = client.get("/v1/me/flows", headers=_HDR)
    assert r2.status_code == 200, r2.text
    items = r2.json()["items"]
    assert any(x["id"] == fid for x in items)

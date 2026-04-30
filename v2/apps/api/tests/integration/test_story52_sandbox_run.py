"""Story 5.2: persistencia sandbox-run com draft real (CI postgres)."""

from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

TENANT = "11111111-1111-4111-8111-111111111111"
_HDR = {"X-Dev-Tenant-Id": TENANT, "X-Dev-Roles": "operator"}

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL") or not os.getenv("ALEMBIC_SYNC_URL"),
    reason="needs DATABASE_URL and ALEMBIC_SYNC_URL (CI postgres)",
)


def _minimal_valid() -> dict:
    return {
        "nodes": [
            {"id": "t_sb", "kind": "trigger"},
            {"id": "a_sb", "kind": "action"},
        ],
        "edges": [{"source": "t_sb", "target": "a_sb"}],
    }


def _sync_engine():
    """Superuser URL em CI; driver psycopg3 (pacote `psycopg`)."""
    u = os.environ["ALEMBIC_SYNC_URL"].replace(
        "postgresql://",
        "postgresql+psycopg://",
        1,
    )
    return create_engine(u)


@pytest.mark.integration
def test_sandbox_run_persists_row_for_draft_uuid(client: TestClient) -> None:
    name = "sandbox-draft-int"
    r = client.post(
        "/v1/me/flows",
        headers=_HDR,
        json={"name": name, "definition": _minimal_valid()},
    )
    assert r.status_code == 201, r.text
    fid = r.json()["id"]
    fixture = {"type": "text", "body": "integration-hi"}
    r2 = client.post(
        f"/v1/me/flows/{fid}/sandbox-run",
        headers=_HDR,
        params={"environment": "sandbox"},
        json={"fixture_message": fixture},
    )
    assert r2.status_code == 200, r2.text
    data = r2.json()
    assert data["persisted"] is True
    run_uuid = uuid.UUID(data["run_id"])
    eng = _sync_engine()
    with eng.connect() as conn:
        row = conn.execute(
            text(
                "SELECT id, correlation_id FROM tenant_flow_sandbox_runs "
                "WHERE id = CAST(:rid AS uuid) AND tenant_id = CAST(:tid AS uuid)",
            ),
            {"rid": str(run_uuid), "tid": TENANT},
        ).fetchone()
    assert row is not None
    assert row[1] == data["correlation_id"]


@pytest.mark.integration
def test_sandbox_run_draft_not_visible_other_tenant(client: TestClient) -> None:
    name = "sandbox-draft-other-tenant"
    r = client.post(
        "/v1/me/flows",
        headers=_HDR,
        json={"name": name, "definition": _minimal_valid()},
    )
    assert r.status_code == 201, r.text
    fid = r.json()["id"]
    other = "22222222-2222-4222-8222-222222222222"
    r2 = client.post(
        f"/v1/me/flows/{fid}/sandbox-run",
        headers={**_HDR, "X-Dev-Tenant-Id": other},
        params={"environment": "sandbox"},
        json={"fixture_message": {"type": "text"}},
    )
    assert r2.status_code == 404, r2.text

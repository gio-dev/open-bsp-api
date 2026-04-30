"""Story 5.3: persistencia publish + audit (Postgres CI)."""

from __future__ import annotations

import os
import uuid

import psycopg
import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL") or not os.getenv("ALEMBIC_SYNC_URL"),
    reason="needs DATABASE_URL and ALEMBIC_SYNC_URL (CI postgres)",
)

TENANT = "11111111-1111-4111-8111-111111111111"
_HDR_OP = {"X-Dev-Tenant-Id": TENANT, "X-Dev-Roles": "operator"}


def _minimal_valid() -> dict:
    return {
        "nodes": [
            {"id": "t_pub", "kind": "trigger"},
            {"id": "a_pub", "kind": "action"},
        ],
        "edges": [{"source": "t_pub", "target": "a_pub"}],
    }


def _sandbox_succeeded(client: TestClient, flow_id: str) -> None:
    r = client.post(
        f"/v1/me/flows/{flow_id}/sandbox-run",
        headers=_HDR_OP,
        params={"environment": "sandbox"},
        json={"fixture_message": {"type": "text", "body": "pub-pre"}},
    )
    assert r.status_code == 200, r.text
    assert r.json().get("status") == "succeeded"


@pytest.mark.integration
def test_publish_staging_inserts_activation_and_audit(client: TestClient) -> None:
    admin_url = os.environ["ALEMBIC_SYNC_URL"]
    with psycopg.connect(admin_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM audit_events WHERE tenant_id = %s::uuid "
                "AND resource_type = 'flow_publish'",
                (TENANT,),
            )
            a0 = cur.fetchone()[0]

    name = f"publish-int-{uuid.uuid4().hex[:8]}"
    r = client.post(
        "/v1/me/flows",
        headers=_HDR_OP,
        json={"name": name, "definition": _minimal_valid()},
    )
    assert r.status_code == 201, r.text
    fid = r.json()["id"]
    _sandbox_succeeded(client, fid)

    r2 = client.post(
        f"/v1/me/flows/{fid}/publish",
        headers=_HDR_OP,
        json={"environment": "staging"},
    )
    assert r2.status_code == 200, r2.text

    with psycopg.connect(admin_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM tenant_flow_publish_activations "
                "WHERE tenant_id = %s::uuid AND flow_draft_id = %s::uuid "
                "AND environment = 'staging'",
                (TENANT, fid),
            )
            assert cur.fetchone()[0] == 1
            cur.execute(
                "SELECT count(*) FROM audit_events WHERE tenant_id = %s::uuid "
                "AND resource_type = 'flow_publish'",
                (TENANT,),
            )
            a1 = cur.fetchone()[0]
            cur.execute(
                "SELECT count(*) FROM tenant_flow_publish_versions "
                "WHERE tenant_id = %s::uuid AND flow_draft_id = %s::uuid "
                "AND environment = 'staging'",
                (TENANT, fid),
            )
            assert cur.fetchone()[0] == 1
    assert a1 == a0 + 1


@pytest.mark.integration
def test_publish_repeat_same_definition_idempotent_audit_unchanged(
    client: TestClient,
) -> None:
    admin_url = os.environ["ALEMBIC_SYNC_URL"]
    name = f"publish-idem-{uuid.uuid4().hex[:8]}"
    r = client.post(
        "/v1/me/flows",
        headers=_HDR_OP,
        json={"name": name, "definition": _minimal_valid()},
    )
    assert r.status_code == 201, r.text
    fid = r.json()["id"]
    _sandbox_succeeded(client, fid)

    with psycopg.connect(admin_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM audit_events WHERE tenant_id = %s::uuid "
                "AND resource_type = 'flow_publish'",
                (TENANT,),
            )
            a0 = cur.fetchone()[0]
            cur.execute(
                "SELECT count(*) FROM tenant_flow_publish_versions "
                "WHERE tenant_id = %s::uuid AND flow_draft_id = %s::uuid",
                (TENANT, fid),
            )
            v0 = cur.fetchone()[0]

    r1 = client.post(
        f"/v1/me/flows/{fid}/publish",
        headers=_HDR_OP,
        json={"environment": "staging"},
    )
    assert r1.status_code == 200, r1.text
    assert r1.json().get("idempotent_repeat") is False
    r2 = client.post(
        f"/v1/me/flows/{fid}/publish",
        headers=_HDR_OP,
        json={"environment": "staging"},
    )
    assert r2.status_code == 200, r2.text
    assert r2.json().get("idempotent_repeat") is True

    with psycopg.connect(admin_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM audit_events WHERE tenant_id = %s::uuid "
                "AND resource_type = 'flow_publish'",
                (TENANT,),
            )
            a1 = cur.fetchone()[0]
            cur.execute(
                "SELECT count(*) FROM tenant_flow_publish_versions "
                "WHERE tenant_id = %s::uuid AND flow_draft_id = %s::uuid",
                (TENANT, fid),
            )
            v1 = cur.fetchone()[0]
    assert a1 == a0 + 1
    assert v1 == v0 + 1


@pytest.mark.integration
def test_publish_without_prior_sandbox_returns_422(client: TestClient) -> None:
    name = f"publish-nosb-{uuid.uuid4().hex[:8]}"
    r = client.post(
        "/v1/me/flows",
        headers=_HDR_OP,
        json={"name": name, "definition": _minimal_valid()},
    )
    assert r.status_code == 201, r.text
    fid = r.json()["id"]
    r2 = client.post(
        f"/v1/me/flows/{fid}/publish",
        headers=_HDR_OP,
        json={"environment": "staging"},
    )
    assert r2.status_code == 422, r2.text
    errs = r2.json().get("errors") or []
    assert any(e.get("field") == "flow_id" for e in errs)


@pytest.mark.integration
def test_publish_draft_not_visible_other_tenant_returns_404(
    client: TestClient,
) -> None:
    name = f"publish-xtenant-{uuid.uuid4().hex[:8]}"
    r = client.post(
        "/v1/me/flows",
        headers=_HDR_OP,
        json={"name": name, "definition": _minimal_valid()},
    )
    assert r.status_code == 201, r.text
    fid = r.json()["id"]
    other = "22222222-2222-4222-8222-222222222222"
    r2 = client.post(
        f"/v1/me/flows/{fid}/publish",
        headers={**_HDR_OP, "X-Dev-Tenant-Id": other},
        json={"environment": "development"},
    )
    assert r2.status_code == 404, r2.text

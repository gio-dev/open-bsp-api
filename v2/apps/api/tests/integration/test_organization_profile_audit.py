"""Organization PATCH audit + cross-tenant isolation (Story 1.3)."""

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

_T1 = "11111111-1111-4111-8111-111111111111"
_HEADERS_T1: dict[str, str] = {
    "X-Dev-Tenant-Id": _T1,
    "X-Dev-User-Id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
    "X-Dev-Roles": "org_admin",
}


@pytest.mark.integration
def test_patch_organization_appends_audit_event(client: TestClient) -> None:
    admin_url = os.environ["ALEMBIC_SYNC_URL"]
    with psycopg.connect(admin_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM audit_events WHERE tenant_id = %s::uuid",
                (_T1,),
            )
            n0 = cur.fetchone()[0]

    tag = str(uuid.uuid4())[:8]
    r = client.patch(
        "/v1/me/organization",
        headers=_HEADERS_T1,
        json={"display_name": f"audit-event-{tag}"},
    )
    assert r.status_code == 200, r.text

    with psycopg.connect(admin_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM audit_events WHERE tenant_id = %s::uuid",
                (_T1,),
            )
            n1 = cur.fetchone()[0]
    assert n1 == n0 + 1


@pytest.mark.integration
def test_patch_organization_noop_does_not_add_audit(client: TestClient) -> None:
    admin_url = os.environ["ALEMBIC_SYNC_URL"]
    g = client.get("/v1/me/organization", headers=_HEADERS_T1)
    assert g.status_code == 200, g.text
    name = g.json()["display_name"]

    with psycopg.connect(admin_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM audit_events WHERE tenant_id = %s::uuid",
                (_T1,),
            )
            n0 = cur.fetchone()[0]

    r = client.patch(
        "/v1/me/organization",
        headers=_HEADERS_T1,
        json={"display_name": name},
    )
    assert r.status_code == 200, r.text

    with psycopg.connect(admin_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM audit_events WHERE tenant_id = %s::uuid",
                (_T1,),
            )
            n1 = cur.fetchone()[0]
    assert n1 == n0


@pytest.mark.integration
def test_patch_tenant_one_does_not_change_tenant_two_settings(
    client: TestClient,
) -> None:
    admin_url = os.environ["ALEMBIC_SYNC_URL"]
    t2 = uuid.uuid4()
    row2 = uuid.uuid4()

    with psycopg.connect(admin_url, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO tenants (id) VALUES (%s)", (str(t2),))
            cur.execute(
                "INSERT INTO tenant_settings_stub (id, tenant_id, display_name) "
                "VALUES (%s, %s, %s)",
                (str(row2), str(t2), "OTHER-TENANT-NAME"),
            )

    try:
        tag = str(uuid.uuid4())[:8]
        r = client.patch(
            "/v1/me/organization",
            headers=_HEADERS_T1,
            json={"display_name": f"only-t1-{tag}"},
        )
        assert r.status_code == 200, r.text

        with psycopg.connect(admin_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT display_name FROM tenant_settings_stub "
                    "WHERE tenant_id = %s::uuid",
                    (str(t2),),
                )
                other = cur.fetchone()
        assert other is not None
        assert other[0] == "OTHER-TENANT-NAME"
    finally:
        with psycopg.connect(admin_url, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM tenant_settings_stub WHERE tenant_id = %s::uuid",
                    (str(t2),),
                )
                cur.execute("DELETE FROM tenants WHERE id = %s::uuid", (str(t2),))

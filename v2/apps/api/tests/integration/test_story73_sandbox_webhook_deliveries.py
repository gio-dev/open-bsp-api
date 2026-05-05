"""Story 7.3: webhook delivery log tenant-scoped (RLS) + RBAC lista."""

from __future__ import annotations

import os
import uuid

import psycopg
import pytest
from fastapi.testclient import TestClient

TENANT = "11111111-1111-4111-8111-111111111111"
TENANT_B = "22222222-2222-4222-8222-222222222222"
CONSOLE_USER = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL") or not os.getenv("ALEMBIC_SYNC_URL"),
    reason="needs DATABASE_URL and ALEMBIC_SYNC_URL (CI postgres)",
)


def _ensure_tenant_b(dsn: str) -> None:
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tenants (id) VALUES (%s::uuid) ON CONFLICT DO NOTHING",
                (TENANT_B,),
            )
            cur.execute(
                """
                INSERT INTO tenant_memberships (id, user_id, tenant_id, role)
                VALUES (%s::uuid, %s::uuid, %s::uuid, 'org_admin')
                ON CONFLICT ON CONSTRAINT uq_tenant_memberships_user_tenant
                DO NOTHING
                """,
                (str(uuid.uuid4()), CONSOLE_USER, TENANT_B),
            )
        conn.commit()


@pytest.mark.integration
def test_sandbox_webhook_deliveries_cross_tenant_isolated(
    client: TestClient,
) -> None:
    dsn = os.environ["ALEMBIC_SYNC_URL"]
    _ensure_tenant_b(dsn)
    rid_a = f"story73-a-{uuid.uuid4()}"
    rid_b = f"story73-b-{uuid.uuid4()}"
    try:
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO tenant_sandbox_webhook_deliveries
                      (tenant_id, request_id, status, enqueued, deduplicated, skipped)
                    VALUES (%s::uuid, %s, 'accepted', 2, 1, 0)
                    """,
                    (TENANT, rid_a),
                )
                cur.execute(
                    """
                    INSERT INTO tenant_sandbox_webhook_deliveries
                      (tenant_id, request_id, status, enqueued, deduplicated, skipped)
                    VALUES (%s::uuid, %s, 'accepted', 0, 0, 3)
                    """,
                    (TENANT_B, rid_b),
                )
            conn.commit()

        ha = {"X-Dev-Tenant-Id": TENANT, "X-Dev-Roles": "org_admin"}
        hb = {"X-Dev-Tenant-Id": TENANT_B, "X-Dev-Roles": "org_admin"}

        ra = client.get("/v1/me/sandbox/webhook-deliveries", headers=ha)
        assert ra.status_code == 200, ra.text
        ids_a = {x["request_id"] for x in ra.json()["items"]}
        assert rid_a in ids_a
        assert rid_b not in ids_a

        rb = client.get("/v1/me/sandbox/webhook-deliveries", headers=hb)
        assert rb.status_code == 200, rb.text
        ids_b = {x["request_id"] for x in rb.json()["items"]}
        assert rid_b in ids_b
        assert rid_a not in ids_b
    finally:
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM tenant_sandbox_webhook_deliveries "
                    "WHERE request_id IN (%s, %s)",
                    (rid_a, rid_b),
                )
            conn.commit()


@pytest.mark.integration
def test_sandbox_webhook_deliveries_operator_403(client: TestClient) -> None:
    r = client.get(
        "/v1/me/sandbox/webhook-deliveries",
        headers={"X-Dev-Tenant-Id": TENANT, "X-Dev-Roles": "operator"},
    )
    assert r.status_code == 403, r.text

"""Story 8.1: metering daily aggregates tenant-scoped (RLS) + RBAC."""

from __future__ import annotations

import os
import uuid
from datetime import date

import psycopg
import pytest
from app.db.models_usage import USAGE_METRIC_INBOUND_MESSAGES
from fastapi.testclient import TestClient

TENANT = "11111111-1111-4111-8111-111111111111"
TENANT_B = "22222222-2222-4222-8222-222222222222"
CONSOLE_USER = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
_BUCKET = date(2030, 1, 15)

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


def _usage_params() -> str:
    return f"since={_BUCKET.isoformat()}&until={_BUCKET.isoformat()}"


@pytest.mark.integration
def test_usage_summary_cross_tenant_isolated(client: TestClient) -> None:
    dsn = os.environ["ALEMBIC_SYNC_URL"]
    _ensure_tenant_b(dsn)
    try:
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO tenant_metering_daily
                      (tenant_id, bucket_date, metric_key, count)
                    VALUES (%s::uuid, %s::date, %s, %s)
                    ON CONFLICT ON CONSTRAINT
                      uq_tenant_metering_daily_tenant_bucket_metric
                    DO UPDATE SET count = EXCLUDED.count
                    """,
                    (TENANT, _BUCKET, USAGE_METRIC_INBOUND_MESSAGES, 7),
                )
                cur.execute(
                    """
                    INSERT INTO tenant_metering_daily
                      (tenant_id, bucket_date, metric_key, count)
                    VALUES (%s::uuid, %s::date, %s, %s)
                    ON CONFLICT ON CONSTRAINT
                      uq_tenant_metering_daily_tenant_bucket_metric
                    DO UPDATE SET count = EXCLUDED.count
                    """,
                    (TENANT_B, _BUCKET, USAGE_METRIC_INBOUND_MESSAGES, 42),
                )
            conn.commit()

        ha = {"X-Dev-Tenant-Id": TENANT, "X-Dev-Roles": "org_admin"}
        hb = {"X-Dev-Tenant-Id": TENANT_B, "X-Dev-Roles": "org_admin"}

        ra = client.get(f"/v1/me/usage/summary?{_usage_params()}", headers=ha)
        assert ra.status_code == 200, ra.text
        by_key_a = {m["metric_key"]: m["count"] for m in ra.json()["metrics"]}
        assert by_key_a[USAGE_METRIC_INBOUND_MESSAGES] == 7

        rb = client.get(f"/v1/me/usage/summary?{_usage_params()}", headers=hb)
        assert rb.status_code == 200, rb.text
        by_key_b = {m["metric_key"]: m["count"] for m in rb.json()["metrics"]}
        assert by_key_b[USAGE_METRIC_INBOUND_MESSAGES] == 42
    finally:
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM tenant_metering_daily
                    WHERE tenant_id IN (%s::uuid, %s::uuid)
                      AND bucket_date = %s::date
                    """,
                    (TENANT, TENANT_B, _BUCKET),
                )
            conn.commit()


@pytest.mark.integration
def test_usage_summary_operator_403(client: TestClient) -> None:
    r = client.get(
        f"/v1/me/usage/summary?{_usage_params()}",
        headers={"X-Dev-Tenant-Id": TENANT, "X-Dev-Roles": "operator"},
    )
    assert r.status_code == 403, r.text

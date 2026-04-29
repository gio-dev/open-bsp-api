"""Story 4.4: GET channel-health agregado por tenant (RLS)."""

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
_HDR = {"X-Dev-Tenant-Id": TENANT, "X-Dev-Roles": "org_admin"}


@pytest.mark.integration
def test_channel_health_shape_and_tenant_scoped(client: TestClient) -> None:
    r = client.get("/v1/me/channel-health", headers=_HDR)
    assert r.status_code == 200, r.text
    data = r.json()
    assert isinstance(data["healthy"], bool)
    assert isinstance(data["incidents"], list)
    c = data["counts"]
    for key in (
        "outbound_failed_meta",
        "outbound_failed_platform",
        "outbound_rate_limited",
        "outbound_stale_queued",
        "handoff_failed",
    ):
        assert key in c
        assert isinstance(c[key], int)


@pytest.mark.integration
def test_channel_health_incidents_isolated_per_tenant(
    client: TestClient,
) -> None:
    """AC2: contagens de falha de outro tenant nao aparecem (NFR-OPS-05)."""
    admin = os.environ["ALEMBIC_SYNC_URL"]
    tenant_empty = uuid.uuid4()
    tenant_b = uuid.uuid4()
    waba_b = uuid.uuid4()
    msg_b = uuid.uuid4()
    phone_id = f"iso-{msg_b.hex[:20]}"
    try:
        with psycopg.connect(admin, autocommit=True) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO tenants (id) VALUES (%s), (%s)",
                (str(tenant_empty), str(tenant_b)),
            )
            cur.execute(
                """
                INSERT INTO waba_phone_numbers
                  (id, tenant_id, waba_id, phone_number_id, display_phone_number,
                   environment, status)
                VALUES (%s::uuid, %s::uuid, %s, %s, %s, %s, 'active')
                """,
                (
                    str(waba_b),
                    str(tenant_b),
                    f"waba-{tenant_b.hex[:12]}",
                    phone_id,
                    "+15551112222",
                    "sandbox",
                ),
            )
            cur.execute(
                """
                INSERT INTO outbound_whatsapp_messages
                  (id, tenant_id, waba_phone_id, to_recipient, message_type,
                   payload, status, upstream_fault)
                VALUES (%s::uuid, %s::uuid, %s::uuid, %s, %s, %s::jsonb, %s, %s)
                """,
                (
                    str(msg_b),
                    str(tenant_b),
                    str(waba_b),
                    "+351910000001",
                    "text",
                    '{"body": "x"}',
                    "failed",
                    "meta",
                ),
            )

        r_empty = client.get(
            "/v1/me/channel-health",
            headers={
                "X-Dev-Tenant-Id": str(tenant_empty),
                "X-Dev-Roles": "org_admin",
            },
        )
        assert r_empty.status_code == 200, r_empty.text
        d0 = r_empty.json()
        assert d0["healthy"] is True
        assert d0["counts"]["outbound_failed_meta"] == 0

        r_b = client.get(
            "/v1/me/channel-health",
            headers={
                "X-Dev-Tenant-Id": str(tenant_b),
                "X-Dev-Roles": "org_admin",
            },
        )
        assert r_b.status_code == 200, r_b.text
        db = r_b.json()
        assert db["healthy"] is False
        assert db["counts"]["outbound_failed_meta"] >= 1
        codes = {i["code"] for i in db["incidents"]}
        assert "outbound_failed_meta" in codes
    finally:
        with psycopg.connect(admin, autocommit=True) as conn:
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM outbound_whatsapp_messages WHERE id = %s::uuid",
                (str(msg_b),),
            )
            cur.execute(
                "DELETE FROM waba_phone_numbers WHERE id = %s::uuid",
                (str(waba_b),),
            )
            cur.execute(
                "DELETE FROM tenants WHERE id = %s::uuid OR id = %s::uuid",
                (str(tenant_empty), str(tenant_b)),
            )

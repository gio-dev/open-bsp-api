"""Story 6.3: tenant contact disclosure preferences."""

from __future__ import annotations

import os
import uuid

import psycopg
import pytest
from app.atdd_fixture_ids import ATDD_CONTACT_PREFERENCES_ID
from fastapi.testclient import TestClient

TENANT = "11111111-1111-4111-8111-111111111111"
TENANT_B = "22222222-2222-4222-8222-222222222222"
CONSOLE_USER = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
PHONE_CI = "351910099888"


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
def test_get_preferences_atdd_fixture(client: TestClient) -> None:
    r = client.get(
        f"/v1/me/contacts/{ATDD_CONTACT_PREFERENCES_ID}/preferences",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "viewer",
        },
    )
    assert r.status_code == 200, r.text
    b = r.json()
    assert b["contact_id"] == ATDD_CONTACT_PREFERENCES_ID


@pytest.mark.integration
def test_get_preferences_implicit_defaults_no_row(client: TestClient) -> None:
    cid = "no-prefs-row-" + uuid.uuid4().hex[:8]
    r = client.get(
        f"/v1/me/contacts/{cid}/preferences",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "viewer",
        },
    )
    assert r.status_code == 200, r.text
    b = r.json()
    assert b["contact_id"] == cid
    assert b["marketing_opt_in"] is False
    assert b["transactional_allowed"] is True
    assert b["disclosure_copy_slug"] == "baseline-v1"
    assert b["updated_at"] is None


@pytest.mark.integration
def test_patch_preferences_org_admin(client: TestClient) -> None:
    r1 = client.patch(
        f"/v1/me/contacts/{ATDD_CONTACT_PREFERENCES_ID}/preferences",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "org_admin",
        },
        json={"marketing_opt_in": True},
    )
    assert r1.status_code == 200, r1.text
    assert r1.json()["marketing_opt_in"] is True
    r2 = client.patch(
        f"/v1/me/contacts/{ATDD_CONTACT_PREFERENCES_ID}/preferences",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "org_admin",
        },
        json={"marketing_opt_in": False},
    )
    assert r2.status_code == 200, r2.text


@pytest.mark.integration
def test_patch_preferences_viewer_forbidden(client: TestClient) -> None:
    r = client.patch(
        f"/v1/me/contacts/{ATDD_CONTACT_PREFERENCES_ID}/preferences",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "viewer",
        },
        json={"marketing_opt_in": True},
    )
    assert r.status_code == 403


@pytest.mark.integration
def test_cross_tenant_preferences_isolated(client: TestClient) -> None:
    dsn = os.environ["ALEMBIC_SYNC_URL"]
    _ensure_tenant_b(dsn)
    cid = "rls-" + uuid.uuid4().hex[:10]
    h_a = {"X-Dev-Tenant-Id": TENANT, "X-Dev-Roles": "org_admin"}
    h_b = {"X-Dev-Tenant-Id": TENANT_B, "X-Dev-Roles": "org_admin"}
    try:
        pa = client.patch(
            f"/v1/me/contacts/{cid}/preferences",
            headers=h_a,
            json={
                "marketing_opt_in": True,
                "transactional_allowed": True,
                "disclosure_copy_slug": "tenant-a-slug",
            },
        )
        assert pa.status_code == 200, pa.text
        rb = client.get(
            f"/v1/me/contacts/{cid}/preferences",
            headers={**h_b, "X-Dev-Roles": "viewer"},
        )
        assert rb.status_code == 200, rb.text
        body_b = rb.json()
        assert body_b["marketing_opt_in"] is False
        assert body_b["transactional_allowed"] is True
        assert body_b["disclosure_copy_slug"] == "baseline-v1"
    finally:
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM tenant_contact_preferences WHERE contact_id = %s",
                    (cid,),
                )
            conn.commit()


@pytest.mark.integration
def test_send_marketing_respects_preferences(client: TestClient) -> None:
    cid = PHONE_CI
    h = {"X-Dev-Tenant-Id": TENANT, "X-Dev-Roles": "org_admin"}
    try:
        pr = client.patch(
            f"/v1/me/contacts/{cid}/preferences",
            headers=h,
            json={"marketing_opt_in": False, "transactional_allowed": True},
        )
        assert pr.status_code == 200, pr.text
        r_block = client.post(
            "/v1/me/messages/send",
            headers=h,
            json={
                "to": f"+{cid}",
                "type": "text",
                "text": {"body": "m"},
                "environment": "sandbox",
                "preference_kind": "marketing",
            },
        )
        assert r_block.status_code == 409, r_block.text

        pa = client.patch(
            f"/v1/me/contacts/{cid}/preferences",
            headers=h,
            json={"marketing_opt_in": True},
        )
        assert pa.status_code == 200, pa.text
        r_ok = client.post(
            "/v1/me/messages/send",
            headers=h,
            json={
                "to": f"+{cid}",
                "type": "text",
                "text": {"body": "m2"},
                "environment": "sandbox",
                "preference_kind": "marketing",
            },
        )
        assert r_ok.status_code == 202, r_ok.text
    finally:
        client.patch(
            f"/v1/me/contacts/{cid}/preferences",
            headers=h,
            json={"marketing_opt_in": False},
        )


@pytest.mark.integration
def test_send_transactional_allowed_when_marketing_opt_out(client: TestClient) -> None:
    """FR33: transacional pode enviar com marketing desligado."""
    cid = "351910077001"
    h = {"X-Dev-Tenant-Id": TENANT, "X-Dev-Roles": "org_admin"}
    try:
        pr = client.patch(
            f"/v1/me/contacts/{cid}/preferences",
            headers=h,
            json={"marketing_opt_in": False, "transactional_allowed": True},
        )
        assert pr.status_code == 200, pr.text
        r = client.post(
            "/v1/me/messages/send",
            headers=h,
            json={
                "to": f"+{cid}",
                "type": "text",
                "text": {"body": "otp-msg"},
                "environment": "sandbox",
                "preference_kind": "transactional",
            },
        )
        assert r.status_code == 202, r.text
    finally:
        with psycopg.connect(os.environ["ALEMBIC_SYNC_URL"]) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM tenant_contact_preferences WHERE contact_id = %s",
                    (cid,),
                )
            conn.commit()


@pytest.mark.integration
def test_send_transactional_blocked_when_disallowed(client: TestClient) -> None:
    cid = "351910077002"
    h = {"X-Dev-Tenant-Id": TENANT, "X-Dev-Roles": "org_admin"}
    try:
        pr = client.patch(
            f"/v1/me/contacts/{cid}/preferences",
            headers=h,
            json={
                "marketing_opt_in": False,
                "transactional_allowed": False,
            },
        )
        assert pr.status_code == 200, pr.text
        r = client.post(
            "/v1/me/messages/send",
            headers=h,
            json={
                "to": f"+{cid}",
                "type": "text",
                "text": {"body": "tx"},
                "environment": "sandbox",
                "preference_kind": "transactional",
            },
        )
        assert r.status_code == 409, r.text
        assert "transactional_blocked" in r.json().get("message", "")
    finally:
        with psycopg.connect(os.environ["ALEMBIC_SYNC_URL"]) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM tenant_contact_preferences WHERE contact_id = %s",
                    (cid,),
                )
            conn.commit()


@pytest.mark.integration
def test_classified_send_writes_audit_snapshot(client: TestClient) -> None:
    dsn = os.environ["ALEMBIC_SYNC_URL"]
    cid = "351910077003"
    h = {"X-Dev-Tenant-Id": TENANT, "X-Dev-Roles": "org_admin"}
    try:
        client.patch(
            f"/v1/me/contacts/{cid}/preferences",
            headers=h,
            json={"marketing_opt_in": False, "transactional_allowed": True},
        )
        r = client.post(
            "/v1/me/messages/send",
            headers=h,
            json={
                "to": f"+{cid}",
                "type": "text",
                "text": {"body": "aud"},
                "environment": "sandbox",
                "preference_kind": "transactional",
            },
        )
        assert r.status_code == 202, r.text
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    (
                        "SELECT summary FROM audit_events "
                        "WHERE tenant_id = %s::uuid "
                        "AND resource_type = 'whatsapp_outbound_enqueued' "
                        "AND summary LIKE %s ORDER BY created_at DESC LIMIT 1"
                    ),
                    (TENANT, f"%to={cid}%"),
                )
                row = cur.fetchone()
        assert row is not None
        assert "kind=transactional" in row[0]
        assert "m=False" in row[0]
        assert "t=True" in row[0]
    finally:
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM audit_events WHERE tenant_id = %s::uuid "
                    "AND resource_type = 'whatsapp_outbound_enqueued' "
                    "AND summary LIKE %s",
                    (TENANT, f"%to={cid}%"),
                )
                cur.execute(
                    "DELETE FROM tenant_contact_preferences WHERE contact_id = %s",
                    (cid,),
                )
                cur.execute(
                    "DELETE FROM outbound_whatsapp_messages "
                    "WHERE tenant_id = %s::uuid AND to_recipient = %s",
                    (TENANT, cid),
                )
            conn.commit()

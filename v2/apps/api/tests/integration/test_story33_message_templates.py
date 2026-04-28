"""Story 3.3: templates + sinais (cache + refresh)."""

from __future__ import annotations

import os

import psycopg
import pytest
from fastapi.testclient import TestClient

TENANT = "11111111-1111-4111-8111-111111111111"

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL") or not os.getenv("ALEMBIC_SYNC_URL"),
    reason="needs DATABASE_URL and ALEMBIC_SYNC_URL (CI postgres)",
)


@pytest.fixture(autouse=True)
def _clear_wa_template_cache() -> None:
    """Evita estado residual de corridas anteriores (Postgres persistente)."""
    dsn = os.getenv("ALEMBIC_SYNC_URL")
    if not dsn:
        return
    import psycopg

    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM whatsapp_message_templates WHERE tenant_id = %s::uuid",
                (TENANT,),
            )
            cur.execute(
                "DELETE FROM whatsapp_channel_snapshots WHERE tenant_id = %s::uuid",
                (TENANT,),
            )
        conn.commit()


@pytest.mark.integration
def test_message_templates_refresh_failed_preserves_cache(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    r0 = client.get(
        "/v1/me/message-templates",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "org_admin",
        },
        params={"environment": "sandbox", "refresh": "true"},
    )
    assert r0.status_code == 200, r0.text
    n0 = len(r0.json()["items"])
    assert n0 >= 2

    async def _fail_fetch(*_a, **_k):
        return [], False

    monkeypatch.setattr(
        "app.whatsapp.templates_meta.fetch_message_templates",
        _fail_fetch,
    )
    r1 = client.get(
        "/v1/me/message-templates",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "org_admin",
        },
        params={"environment": "sandbox", "refresh": "true"},
    )
    assert r1.status_code == 200, r1.text
    assert len(r1.json()["items"]) >= n0


@pytest.mark.integration
def test_message_templates_multiple_lines_require_phone_number_id(
    client: TestClient,
) -> None:
    extra_row = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa03"
    admin = os.environ["ALEMBIC_SYNC_URL"]
    try:
        with psycopg.connect(admin) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO waba_phone_numbers
                      (id, tenant_id, waba_id, phone_number_id, display_phone_number,
                       environment, status)
                    VALUES (%s::uuid, %s::uuid, %s, %s, %s, %s, 'active')
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        extra_row,
                        TENANT,
                        "ci-atdd-waba",
                        "ci-atdd-phone-2",
                        "+15550004444",
                        "sandbox",
                    ),
                )
            conn.commit()

        r = client.get(
            "/v1/me/message-templates",
            headers={
                "X-Dev-Tenant-Id": TENANT,
                "X-Dev-Roles": "org_admin",
            },
            params={"environment": "sandbox"},
        )
        assert r.status_code == 409, r.text
        assert "phone_number_id" in r.json().get("message", "").lower()

        r2 = client.get(
            "/v1/me/message-templates",
            headers={
                "X-Dev-Tenant-Id": TENANT,
                "X-Dev-Roles": "org_admin",
            },
            params={
                "environment": "sandbox",
                "phone_number_id": "ci-atdd-phone-1",
            },
        )
        assert r2.status_code == 200, r2.text
        assert r2.json().get("waba_id") == "ci-atdd-waba"
    finally:
        with psycopg.connect(admin) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM waba_phone_numbers WHERE id = %s::uuid",
                    (extra_row,),
                )
            conn.commit()


@pytest.mark.integration
def test_message_templates_list_not_synced(client: TestClient) -> None:
    r = client.get(
        "/v1/me/message-templates",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "org_admin",
        },
        params={"environment": "sandbox"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["environment"] == "sandbox"
    assert data["waba_id"] == "ci-atdd-waba"
    assert data["channel_signals"]["source"] == "not_synced"
    assert isinstance(data["items"], list)


@pytest.mark.integration
def test_message_templates_refresh_stub_populates(client: TestClient) -> None:
    r = client.get(
        "/v1/me/message-templates",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "org_admin",
        },
        params={"environment": "sandbox", "refresh": "true"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert len(data["items"]) >= 2
    names = {x["name"] for x in data["items"]}
    assert "ci_welcome" in names and "ci_promo" in names
    assert data["channel_signals"]["source"] == "stub"
    assert data["last_sync_at"] is not None


@pytest.mark.integration
def test_message_templates_refresh_forbidden_for_viewer(client: TestClient) -> None:
    r = client.get(
        "/v1/me/message-templates",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "viewer",
        },
        params={"environment": "sandbox", "refresh": "true"},
    )
    assert r.status_code == 403, r.text

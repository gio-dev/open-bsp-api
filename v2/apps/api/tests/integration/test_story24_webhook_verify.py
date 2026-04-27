"""Story 2.4: rotacao de segredo GET hub + verificacao com tenant_id."""

from __future__ import annotations

import os

import psycopg
import pytest
from fastapi.testclient import TestClient

TENANT = "11111111-1111-4111-8111-111111111111"
HDR = {
    "X-Dev-Tenant-Id": TENANT,
    "X-Dev-User-Id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
    "X-Dev-Roles": "org_admin",
}

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL") or not os.getenv("ALEMBIC_SYNC_URL"),
    reason="needs DATABASE_URL and ALEMBIC_SYNC_URL (CI postgres)",
)


@pytest.mark.integration
def test_rotate_then_hub_verify_tenant_path(client: TestClient) -> None:
    r0 = client.post("/v1/me/webhook-secrets/rotate", headers=HDR, json={})
    assert r0.status_code == 201, r0.text
    token = r0.json()["verify_token"]

    r_hub = client.get(
        "/v1/webhooks/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": token,
            "hub.challenge": "okchallenge",
            "tenant_id": TENANT,
        },
    )
    assert r_hub.status_code == 200, r_hub.text
    assert r_hub.text == "okchallenge"


@pytest.mark.integration
def test_after_coexistence_window_old_verify_token_rejected(
    client: TestClient,
) -> None:
    """Apos invalid_after do antigo, hub GET: v1 403, v2 200."""
    r0 = client.post("/v1/me/webhook-secrets/rotate", headers=HDR, json={})
    assert r0.status_code == 201, r0.text
    token0 = r0.json()["verify_token"]
    r1 = client.post(
        "/v1/me/webhook-secrets/rotate",
        headers=HDR,
        json={"coexistence_seconds": 300},
    )
    assert r1.status_code == 201, r1.text
    token1 = r1.json()["verify_token"]
    assert token0 != token1

    r_ok0 = client.get(
        "/v1/webhooks/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": token0,
            "hub.challenge": "c0",
            "tenant_id": TENANT,
        },
    )
    assert r_ok0.status_code == 200, r_ok0.text

    lr = client.get("/v1/me/webhook-secrets", headers=HDR)
    assert lr.status_code == 200, lr.text
    old_id: str | None = next(
        (it["id"] for it in lr.json()["items"] if it.get("status") == "coexisting"),
        None,
    )
    assert old_id is not None, "expected a coexisting row after rotate with window"

    admin_url = os.environ["ALEMBIC_SYNC_URL"]
    with psycopg.connect(admin_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                (
                    "UPDATE webhook_verify_secrets "
                    "SET invalid_after = NOW() - interval '1 minute' "
                    "WHERE id = %s::uuid"
                ),
                (old_id,),
            )
        conn.commit()

    r403 = client.get(
        "/v1/webhooks/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": token0,
            "hub.challenge": "c0",
            "tenant_id": TENANT,
        },
    )
    assert r403.status_code == 403, r403.text

    r_ok1 = client.get(
        "/v1/webhooks/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": token1,
            "hub.challenge": "c1",
            "tenant_id": TENANT,
        },
    )
    assert r_ok1.status_code == 200, r_ok1.text
    assert r_ok1.text == "c1"

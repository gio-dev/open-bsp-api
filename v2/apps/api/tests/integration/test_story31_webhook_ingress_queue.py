"""Story 3.1: fila webhook com tenant resolvido, idempotencia e anti-replay."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time

import psycopg
import pytest
from fastapi.testclient import TestClient

TENANT = "11111111-1111-4111-8111-111111111111"

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL") or not os.getenv("ALEMBIC_SYNC_URL"),
    reason="needs DATABASE_URL and ALEMBIC_SYNC_URL (CI postgres)",
)


def _sign(body: bytes, secret: str) -> str:
    return (
        "sha256=" + hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    )


def _make_payload(source_id: str, ts: int | None = None) -> dict:
    ts = int(time.time()) if ts is None else ts
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "ci-atdd-waba",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {"phone_number_id": "ci-atdd-phone-1"},
                            "messages": [
                                {
                                    "id": source_id,
                                    "from": "15550009999",
                                    "timestamp": str(ts),
                                    "type": "text",
                                    "text": {"body": "hello"},
                                }
                            ],
                        }
                    }
                ],
            }
        ],
    }


@pytest.mark.integration
def test_webhook_enqueues_row(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("WHATSAPP_WEBHOOK_APP_SECRET", "ingress-secret")
    from app.core.config import get_settings

    get_settings.cache_clear()
    admin = os.environ["ALEMBIC_SYNC_URL"]
    uid = f"wamid.test-{time.time_ns()}"
    with psycopg.connect(admin) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM webhook_inbound_events WHERE source_id = %s",
                (uid,),
            )
        conn.commit()

    body = json.dumps(_make_payload(uid)).encode("utf-8")
    r = client.post(
        "/v1/webhooks/whatsapp",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": _sign(body, "ingress-secret"),
        },
    )
    assert r.status_code == 202, r.text
    data = r.json()
    assert data["enqueued"] >= 1
    assert data["request_id"]

    with psycopg.connect(admin) as conn:
        with conn.cursor() as cur:
            cur.execute(
                (
                    "SELECT tenant_id::text, event_kind FROM webhook_inbound_events "
                    "WHERE source_id = %s"
                ),
                (uid,),
            )
            row = cur.fetchone()
    assert row is not None
    assert row[0] == TENANT
    assert row[1] == "message"

    get_settings.cache_clear()
    monkeypatch.delenv("WHATSAPP_WEBHOOK_APP_SECRET", raising=False)


@pytest.mark.integration
def test_webhook_idempotent_same_message_id(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("WHATSAPP_WEBHOOK_APP_SECRET", "ingress-secret-2")
    from app.core.config import get_settings

    get_settings.cache_clear()
    admin = os.environ["ALEMBIC_SYNC_URL"]
    uid = f"wamid.dupe-{time.time_ns()}"
    with psycopg.connect(admin) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM webhook_inbound_events WHERE source_id = %s",
                (uid,),
            )
        conn.commit()

    body = json.dumps(_make_payload(uid)).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": _sign(body, "ingress-secret-2"),
    }
    r1 = client.post("/v1/webhooks/whatsapp", content=body, headers=headers)
    r2 = client.post("/v1/webhooks/whatsapp", content=body, headers=headers)
    assert r1.status_code == 202 and r2.status_code == 202
    assert r1.json()["enqueued"] >= 1
    assert r2.json()["deduplicated"] >= 1
    assert r2.json()["enqueued"] == 0

    with psycopg.connect(admin) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM webhook_inbound_events WHERE source_id = %s",
                (uid,),
            )
            n = cur.fetchone()[0]
    assert n == 1

    get_settings.cache_clear()
    monkeypatch.delenv("WHATSAPP_WEBHOOK_APP_SECRET", raising=False)


@pytest.mark.integration
def test_webhook_rejects_stale_timestamp(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("WHATSAPP_WEBHOOK_APP_SECRET", "ingress-secret-3")
    from app.core.config import get_settings

    get_settings.cache_clear()
    uid = f"wamid.old-{time.time_ns()}"
    body = json.dumps(_make_payload(uid, ts=1600000000)).encode("utf-8")
    r = client.post(
        "/v1/webhooks/whatsapp",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": _sign(body, "ingress-secret-3"),
        },
    )
    assert r.status_code == 409, r.text

    get_settings.cache_clear()
    monkeypatch.delenv("WHATSAPP_WEBHOOK_APP_SECRET", raising=False)


@pytest.mark.integration
def test_webhook_ambiguous_waba_returns_409(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Dois tenants com o mesmo waba_id sem phone_number_id no payload -> 409."""
    monkeypatch.setenv("WHATSAPP_WEBHOOK_APP_SECRET", "ingress-secret-amb")
    from app.core.config import get_settings

    get_settings.cache_clear()
    admin = os.environ["ALEMBIC_SYNC_URL"]
    tenant_b = "44444444-4444-4444-8444-444444444444"
    waba_row_b = "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee"
    settings_row_b = "ffffffff-ffff-4fff-8fff-ffffffffffff"
    uid = f"wamid.amb-{time.time_ns()}"
    try:
        with psycopg.connect(admin) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO tenants (id) VALUES (%s::uuid) ON CONFLICT DO NOTHING",
                    (tenant_b,),
                )
                cur.execute(
                    """
                    INSERT INTO tenant_settings_stub
                      (id, tenant_id, display_name, timezone, operational_email)
                    VALUES (%s::uuid, %s::uuid, %s, %s, %s)
                    ON CONFLICT (tenant_id) DO NOTHING
                    """,
                    (settings_row_b, tenant_b, "Ambiguous B", "Europe/Lisbon", ""),
                )
                cur.execute(
                    """
                    INSERT INTO waba_phone_numbers
                      (id, tenant_id, waba_id, phone_number_id, display_phone_number,
                       environment, status)
                    VALUES (%s::uuid, %s::uuid, %s, %s, %s, %s, 'active')
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        waba_row_b,
                        tenant_b,
                        "ci-atdd-waba",
                        "ci-atdd-phone-ambiguous-b",
                        "+15550002222",
                        "sandbox",
                    ),
                )
            conn.commit()

        pl = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "ci-atdd-waba",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {},
                                "messages": [
                                    {
                                        "id": uid,
                                        "from": "15550009999",
                                        "timestamp": str(int(time.time())),
                                        "type": "text",
                                        "text": {"body": "amb"},
                                    }
                                ],
                            }
                        }
                    ],
                }
            ],
        }
        body = json.dumps(pl).encode("utf-8")
        r = client.post(
            "/v1/webhooks/whatsapp",
            content=body,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": _sign(body, "ingress-secret-amb"),
            },
        )
        assert r.status_code == 409, r.text
        assert "ambiguous" in r.json().get("message", "").lower()
    finally:
        with psycopg.connect(admin) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM waba_phone_numbers WHERE id = %s::uuid",
                    (waba_row_b,),
                )
                cur.execute(
                    "DELETE FROM tenant_settings_stub WHERE tenant_id = %s::uuid",
                    (tenant_b,),
                )
                cur.execute("DELETE FROM tenants WHERE id = %s::uuid", (tenant_b,))
            conn.commit()

        get_settings.cache_clear()
        monkeypatch.delenv("WHATSAPP_WEBHOOK_APP_SECRET", raising=False)


@pytest.mark.integration
def test_webhook_rejects_missing_timestamp(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("WHATSAPP_WEBHOOK_APP_SECRET", "ingress-secret-ts")
    from app.core.config import get_settings

    get_settings.cache_clear()
    uid = f"wamid.not-{time.time_ns()}"
    pl = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "ci-atdd-waba",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {"phone_number_id": "ci-atdd-phone-1"},
                            "messages": [
                                {
                                    "id": uid,
                                    "from": "15550009999",
                                    "type": "text",
                                    "text": {"body": "no ts"},
                                }
                            ],
                        }
                    }
                ],
            }
        ],
    }
    body = json.dumps(pl).encode("utf-8")
    r = client.post(
        "/v1/webhooks/whatsapp",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": _sign(body, "ingress-secret-ts"),
        },
    )
    assert r.status_code == 400, r.text
    assert "timestamp" in r.json().get("message", "").lower()

    get_settings.cache_clear()
    monkeypatch.delenv("WHATSAPP_WEBHOOK_APP_SECRET", raising=False)


@pytest.mark.integration
def test_webhook_unknown_waba_returns_404(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("WHATSAPP_WEBHOOK_APP_SECRET", "ingress-secret-4")
    from app.core.config import get_settings

    get_settings.cache_clear()
    pl = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "unknown-waba-xx",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {"phone_number_id": "x"},
                            "messages": [
                                {
                                    "id": "wamid.x",
                                    "timestamp": str(int(time.time())),
                                    "type": "text",
                                    "text": {"body": "z"},
                                }
                            ],
                        }
                    }
                ],
            }
        ],
    }
    body = json.dumps(pl).encode("utf-8")
    r = client.post(
        "/v1/webhooks/whatsapp",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": _sign(body, "ingress-secret-4"),
        },
    )
    assert r.status_code == 404, r.text

    get_settings.cache_clear()
    monkeypatch.delenv("WHATSAPP_WEBHOOK_APP_SECRET", raising=False)

"""Story 3.2: envio outbound + estado + 429 retry."""

from __future__ import annotations

import os
import subprocess
import sys

import psycopg
import pytest
from app.whatsapp.meta_send import MetaSendResult
from fastapi.testclient import TestClient

TENANT = "11111111-1111-4111-8111-111111111111"

_RUN_SWEEP_ONCE = (
    "import asyncio\n"
    "import app.main\n"
    "from app.whatsapp.outbound_sweep import run_outbound_sweep_once\n"
    "asyncio.run(run_outbound_sweep_once())\n"
)

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL") or not os.getenv("ALEMBIC_SYNC_URL"),
    reason="needs DATABASE_URL and ALEMBIC_SYNC_URL (CI postgres)",
)


@pytest.mark.integration
def test_send_message_persists_and_worker_sends_stub(client: TestClient) -> None:
    r = client.post(
        "/v1/me/messages/send",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "org_admin",
        },
        json={
            "to": "+351910000099",
            "type": "text",
            "text": {"body": "integration-outbound"},
            "environment": "sandbox",
        },
    )
    assert r.status_code == 202, r.text
    data = r.json()
    assert data["status"] in ("queued", "sent", "rate_limited", "failed")
    assert "id" in data


@pytest.mark.integration
def test_send_rate_limited_sets_next_attempt(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def _fake_send(**_kwargs):
        return MetaSendResult(
            ok=False,
            http_status=429,
            error_code="rate_limited",
            error_message="too many",
            retry_after_seconds=42,
        )

    monkeypatch.setattr(
        "app.whatsapp.outbound_worker.send_whatsapp_text",
        _fake_send,
    )
    r = client.post(
        "/v1/me/messages/send",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "agent",
        },
        json={
            "to": "+351910000011",
            "type": "text",
            "text": {"body": "rate-limit-test"},
            "environment": "sandbox",
        },
    )
    assert r.status_code == 202, r.text
    mid = r.json()["id"]
    import psycopg

    admin = os.environ["ALEMBIC_SYNC_URL"]
    with psycopg.connect(admin) as conn:
        with conn.cursor() as cur:
            cur.execute(
                (
                    "SELECT status, next_attempt_at IS NOT NULL, upstream_fault "
                    "FROM outbound_whatsapp_messages WHERE id = %s::uuid"
                ),
                (mid,),
            )
            row = cur.fetchone()
    assert row is not None
    assert row[0] == "rate_limited"
    assert row[1] is True
    assert row[2] == "meta"


@pytest.mark.integration
def test_send_idempotency_returns_same_id(
    client: TestClient,
) -> None:
    import time

    key = f"idem-story32-{time.time_ns()}"
    headers = {
        "X-Dev-Tenant-Id": TENANT,
        "X-Dev-Roles": "operator",
        "Idempotency-Key": key,
    }
    body = {
        "to": "+351920000022",
        "type": "text",
        "text": {"body": "idempotent"},
        "environment": "sandbox",
    }
    r1 = client.post("/v1/me/messages/send", headers=headers, json=body)
    r2 = client.post("/v1/me/messages/send", headers=headers, json=body)
    assert r1.status_code == 202 and r2.status_code == 202
    assert r1.json()["id"] == r2.json()["id"]


@pytest.mark.integration
def test_sweep_retries_rate_limited_message(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = {"n": 0}

    async def _fake_send(**_kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            return MetaSendResult(
                ok=False,
                http_status=429,
                error_code="rate_limited",
                error_message="too many",
                retry_after_seconds=7,
            )
        return MetaSendResult(
            ok=True, meta_message_id="wamid.sweep-retry", http_status=200
        )

    monkeypatch.setattr(
        "app.whatsapp.outbound_worker.send_whatsapp_text",
        _fake_send,
    )
    r = client.post(
        "/v1/me/messages/send",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "operator",
        },
        json={
            "to": "+351910000033",
            "type": "text",
            "text": {"body": "sweep-retry"},
            "environment": "sandbox",
        },
    )
    assert r.status_code == 202, r.text
    mid = r.json()["id"]
    assert calls["n"] == 1

    admin = os.environ["ALEMBIC_SYNC_URL"]
    with psycopg.connect(admin) as conn:
        with conn.cursor() as cur:
            cur.execute(
                (
                    "UPDATE outbound_whatsapp_messages "
                    "SET next_attempt_at = now() - interval '2 seconds' "
                    "WHERE id = %s::uuid"
                ),
                (mid,),
            )
        conn.commit()

    subprocess.run([sys.executable, "-c", _RUN_SWEEP_ONCE], check=True)

    with psycopg.connect(admin) as conn:
        with conn.cursor() as cur:
            cur.execute(
                (
                    "SELECT status, meta_message_id "
                    "FROM outbound_whatsapp_messages "
                    "WHERE id = %s::uuid"
                ),
                (mid,),
            )
            row = cur.fetchone()
    assert row is not None
    assert row[0] == "sent"
    assert row[1] is not None


@pytest.mark.integration
def test_multiple_active_senders_requires_phone_number_id(
    client: TestClient,
) -> None:
    import psycopg

    admin = os.environ["ALEMBIC_SYNC_URL"]
    extra_id = "99999999-9999-4999-8999-999999999999"
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
                        extra_id,
                        TENANT,
                        "ci-atdd-waba-second-line",
                        "ci-atdd-phone-2",
                        "+15550003333",
                        "sandbox",
                    ),
                )
            conn.commit()

        r = client.post(
            "/v1/me/messages/send",
            headers={
                "X-Dev-Tenant-Id": TENANT,
                "X-Dev-Roles": "org_admin",
            },
            json={
                "to": "+351910000044",
                "type": "text",
                "text": {"body": "ambiguous-sender"},
                "environment": "sandbox",
            },
        )
        assert r.status_code == 409, r.text
        assert "phone_number_id" in r.json().get("message", "").lower()
    finally:
        with psycopg.connect(admin) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM waba_phone_numbers WHERE id = %s::uuid",
                    (extra_id,),
                )
            conn.commit()

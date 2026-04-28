"""Story 4.3: handoff contexto minimo."""

from __future__ import annotations

import os

import psycopg
import pytest
from fastapi.testclient import TestClient

TENANT = "11111111-1111-4111-8111-111111111111"
USER_A = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
USER_B = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL") or not os.getenv("ALEMBIC_SYNC_URL"),
    reason="needs DATABASE_URL and ALEMBIC_SYNC_URL (CI postgres)",
)


def _seed_handoff_row(dsn: str) -> None:
    """Restaura linha ATDD (idempotente)."""
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO inbox_conversation_handoffs
                  (conversation_id, tenant_id, intent_summary, bot_last_output,
                   handoff_state, queue_id, claimed_by_user_id)
                VALUES (%s, %s::uuid, %s, %s, %s, %s, NULL)
                ON CONFLICT (conversation_id) DO UPDATE SET
                  intent_summary = EXCLUDED.intent_summary,
                  bot_last_output = EXCLUDED.bot_last_output,
                  handoff_state = EXCLUDED.handoff_state,
                  queue_id = EXCLUDED.queue_id,
                  claimed_by_user_id = NULL,
                  updated_at = now()
                """,
                (
                    "atdd-conv-1",
                    TENANT,
                    "Cliente pede atendimento humano (ATDD).",
                    "A transferir para um agente.",
                    "queued",
                    "atdd-queue-default",
                ),
            )
        conn.commit()


@pytest.fixture(autouse=True)
def _reset_handoff_fixture() -> None:
    dsn = os.getenv("ALEMBIC_SYNC_URL")
    if not dsn:
        yield
        return
    _seed_handoff_row(dsn)
    yield
    _seed_handoff_row(dsn)


@pytest.mark.integration
def test_get_handoff_returns_seed_context(client: TestClient) -> None:
    r = client.get(
        "/v1/me/conversations/atdd-conv-1/handoff",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "viewer",
        },
        params={"environment": "sandbox"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["conversation_id"] == "atdd-conv-1"
    assert body["handoff_state"] == "queued"
    assert "humano" in (body["intent_summary"] or "").lower()
    assert body["queue_id"] == "atdd-queue-default"


@pytest.mark.integration
def test_patch_accept_handoff_operator(client: TestClient) -> None:
    r = client.patch(
        "/v1/me/conversations/atdd-conv-1/handoff",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "operator",
            "X-Dev-User-Id": USER_A,
        },
        params={"environment": "sandbox"},
        json={"accept": True},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["handoff_state"] == "accepted"
    assert body["claimed_by_user_id"] == USER_A


@pytest.mark.integration
def test_patch_accept_requires_user_identity_422(client: TestClient) -> None:
    r = client.patch(
        "/v1/me/conversations/atdd-conv-1/handoff",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "operator",
        },
        params={"environment": "sandbox"},
        json={"accept": True},
    )
    assert r.status_code == 422, r.text
    assert "identity" in r.json().get("message", "").lower()


@pytest.mark.integration
def test_patch_accept_idempotent_same_operator(client: TestClient) -> None:
    r1 = client.patch(
        "/v1/me/conversations/atdd-conv-1/handoff",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "operator",
            "X-Dev-User-Id": USER_A,
        },
        params={"environment": "sandbox"},
        json={"accept": True},
    )
    assert r1.status_code == 200, r1.text
    r2 = client.patch(
        "/v1/me/conversations/atdd-conv-1/handoff",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "operator",
            "X-Dev-User-Id": USER_A,
        },
        params={"environment": "sandbox"},
        json={"accept": True},
    )
    assert r2.status_code == 200, r2.text
    assert r2.json()["claimed_by_user_id"] == USER_A


@pytest.mark.integration
def test_patch_accept_reject_when_automated_422(client: TestClient) -> None:
    dsn = os.environ["ALEMBIC_SYNC_URL"]
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE inbox_conversation_handoffs
                SET handoff_state = 'automated',
                    claimed_by_user_id = NULL
                WHERE conversation_id = %s
                """,
                ("atdd-conv-1",),
            )
        conn.commit()
    r = client.patch(
        "/v1/me/conversations/atdd-conv-1/handoff",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "operator",
            "X-Dev-User-Id": USER_A,
        },
        params={"environment": "sandbox"},
        json={"accept": True},
    )
    assert r.status_code == 422, r.text
    assert "state" in r.json().get("message", "").lower()


@pytest.mark.integration
def test_patch_accept_no_handoff_row_422(client: TestClient) -> None:
    dsn = os.environ["ALEMBIC_SYNC_URL"]
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM inbox_conversation_handoffs WHERE conversation_id = %s",
                ("atdd-conv-1",),
            )
        conn.commit()
    r = client.patch(
        "/v1/me/conversations/atdd-conv-1/handoff",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "operator",
            "X-Dev-User-Id": USER_A,
        },
        params={"environment": "sandbox"},
        json={"accept": True},
    )
    assert r.status_code == 422, r.text
    assert "no handoff" in r.json().get("message", "").lower()


@pytest.mark.integration
def test_patch_queue_org_admin(client: TestClient) -> None:
    r = client.patch(
        "/v1/me/conversations/atdd-conv-1/handoff",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "org_admin",
            "X-Dev-User-Id": USER_A,
        },
        params={"environment": "sandbox"},
        json={"queue_id": "sales-line"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["queue_id"] == "sales-line"


@pytest.mark.integration
def test_patch_queue_forbidden_for_operator(client: TestClient) -> None:
    r = client.patch(
        "/v1/me/conversations/atdd-conv-1/handoff",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "operator",
            "X-Dev-User-Id": USER_A,
        },
        params={"environment": "sandbox"},
        json={"queue_id": "x"},
    )
    assert r.status_code == 403, r.text


@pytest.mark.integration
def test_get_handoff_unknown_conversation_404(client: TestClient) -> None:
    r = client.get(
        "/v1/me/conversations/does-not-exist/handoff",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "agent",
        },
        params={"environment": "sandbox"},
    )
    assert r.status_code == 404, r.text


@pytest.mark.integration
def test_patch_accept_conflict_second_operator(client: TestClient) -> None:
    client.patch(
        "/v1/me/conversations/atdd-conv-1/handoff",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "operator",
            "X-Dev-User-Id": USER_A,
        },
        params={"environment": "sandbox"},
        json={"accept": True},
    )
    r2 = client.patch(
        "/v1/me/conversations/atdd-conv-1/handoff",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "operator",
            "X-Dev-User-Id": USER_B,
        },
        params={"environment": "sandbox"},
        json={"accept": True},
    )
    assert r2.status_code == 409, r2.text

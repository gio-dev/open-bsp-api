"""Story 6.2: GET conversa mode (bot/humano) - dados isolados por teste."""

from __future__ import annotations

import os
import uuid
from uuid import UUID

import psycopg
import pytest
from fastapi.testclient import TestClient
from app.inbox.sync import derived_conversation_id

TENANT = "11111111-1111-4111-8111-111111111111"
WABA_PHONE_PK = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL") or not os.getenv("ALEMBIC_SYNC_URL"),
    reason="needs DATABASE_URL and ALEMBIC_SYNC_URL (CI postgres)",
)


def _headers() -> dict[str, str]:
    return {
        "X-Dev-Tenant-Id": TENANT,
        "X-Dev-Roles": "viewer",
    }


def _insert_conversation_with_handoff(
    dsn: str,
    *,
    contact_wa_id: str,
    handoff_state: str,
) -> str:
    cid = derived_conversation_id(
        UUID(TENANT),
        "ci-atdd-waba",
        contact_wa_id,
    )
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO inbox_conversations
                  (id, tenant_id, waba_id, contact_wa_id, environment, title,
                   waba_phone_number_id, last_activity_at)
                VALUES (%s, %s::uuid, %s, %s, %s, %s, %s::uuid, now())
                ON CONFLICT ON CONSTRAINT uq_inbox_conv_tenant_waba_contact DO NOTHING
                """,
                (
                    cid,
                    TENANT,
                    "ci-atdd-waba",
                    contact_wa_id,
                    "sandbox",
                    f"story62-{contact_wa_id}",
                    WABA_PHONE_PK,
                ),
            )
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
                    cid,
                    TENANT,
                    "Story 62 integration.",
                    "Bot output.",
                    handoff_state,
                    "ci-queue-story62",
                ),
            )
        conn.commit()
    return cid


def _delete_conversation(dsn: str, conversation_id: str) -> None:
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM inbox_conversation_handoffs WHERE conversation_id = %s",
                (conversation_id,),
            )
            cur.execute(
                "DELETE FROM inbox_conversations WHERE id = %s",
                (conversation_id,),
            )
        conn.commit()


@pytest.mark.integration
@pytest.mark.parametrize(
    "handoff_state",
    ("pending_handoff", "queued", "accepted", "failed"),
)
def test_get_mode_human_for_pipeline_states(
    client: TestClient,
    handoff_state: str,
) -> None:
    dsn = os.environ["ALEMBIC_SYNC_URL"]
    suffix = uuid.uuid4().hex[:12]
    contact = f"ci62h{suffix}"
    cid = _insert_conversation_with_handoff(
        dsn,
        contact_wa_id=contact,
        handoff_state=handoff_state,
    )
    try:
        r = client.get(
            f"/v1/me/conversations/{cid}/mode",
            headers=_headers(),
            params={"environment": "sandbox"},
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["conversation_id"] == cid
        assert body["mode"] == "human_active"
        assert isinstance(body["since"], str) and len(body["since"]) > 10
        assert "cache-control" in {k.lower() for k in r.headers.keys()}
    finally:
        _delete_conversation(dsn, cid)


@pytest.mark.integration
def test_get_mode_bot_when_automated(client: TestClient) -> None:
    dsn = os.environ["ALEMBIC_SYNC_URL"]
    suffix = uuid.uuid4().hex[:12]
    contact = f"ci62b{suffix}"
    cid = _insert_conversation_with_handoff(
        dsn,
        contact_wa_id=contact,
        handoff_state="automated",
    )
    try:
        r = client.get(
            f"/v1/me/conversations/{cid}/mode",
            headers=_headers(),
            params={"environment": "sandbox"},
        )
        assert r.status_code == 200, r.text
        assert r.json()["mode"] == "bot_active"
    finally:
        _delete_conversation(dsn, cid)


@pytest.mark.integration
def test_get_mode_bot_without_handoff_row(client: TestClient) -> None:
    """Conversa sem linha de handoff => bot_active."""
    dsn = os.environ["ALEMBIC_SYNC_URL"]
    suffix = uuid.uuid4().hex[:12]
    contact = f"ci62n{suffix}"
    cid = derived_conversation_id(UUID(TENANT), "ci-atdd-waba", contact)
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO inbox_conversations
                  (id, tenant_id, waba_id, contact_wa_id, environment, title,
                   waba_phone_number_id, last_activity_at)
                VALUES (%s, %s::uuid, %s, %s, %s, %s, %s::uuid, now())
                ON CONFLICT ON CONSTRAINT uq_inbox_conv_tenant_waba_contact DO NOTHING
                """,
                (
                    cid,
                    TENANT,
                    "ci-atdd-waba",
                    contact,
                    "sandbox",
                    "no-handoff",
                    WABA_PHONE_PK,
                ),
            )
        conn.commit()
    try:
        r = client.get(
            f"/v1/me/conversations/{cid}/mode",
            headers=_headers(),
            params={"environment": "sandbox"},
        )
        assert r.status_code == 200, r.text
        assert r.json()["mode"] == "bot_active"
    finally:
        _delete_conversation(dsn, cid)


@pytest.mark.integration
def test_get_mode_unknown_conversation_404(client: TestClient) -> None:
    r = client.get(
        "/v1/me/conversations/nonexistent-conversation-id-000/mode",
        headers=_headers(),
        params={"environment": "sandbox"},
    )
    assert r.status_code == 404

"""Story 5.5: motor liga ao webhook e pode enfileirar outbound (Postgres CI).

Isolamento: tenant resolve-se via `resolve_waba_tenant` no ingresso; RLS nas sessoes.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
import uuid
from uuid import UUID

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.inbox.sync import derived_conversation_id

TENANT = "11111111-1111-4111-8111-111111111111"
_HDR_OP = {"X-Dev-Tenant-Id": TENANT, "X-Dev-Roles": "operator"}

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL") or not os.getenv("ALEMBIC_SYNC_URL"),
    reason="needs DATABASE_URL and ALEMBIC_SYNC_URL (CI postgres)",
)


def _sign(body: bytes, secret: str) -> str:
    return (
        "sha256=" + hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    )


def _graph_send_text() -> dict:
    return {
        "nodes": [
            {"id": "t_en", "kind": "trigger"},
            {
                "id": "a_en",
                "kind": "action",
                "action_type": "send_text",
                "text_body": "auto from engine",
            },
        ],
        "edges": [{"source": "t_en", "target": "a_en"}],
    }


def _graph_apply_tag(tag_name: str) -> dict:
    return {
        "nodes": [
            {"id": "t_tag", "kind": "trigger"},
            {
                "id": "a_tag",
                "kind": "action",
                "action_type": "apply_tag",
                "tag_name": tag_name,
            },
        ],
        "edges": [{"source": "t_tag", "target": "a_tag"}],
    }


def _graph_handoff() -> dict:
    return {
        "nodes": [
            {"id": "t_ho", "kind": "trigger"},
            {
                "id": "a_ho",
                "kind": "action",
                "action_type": "handoff",
                "handoff_intent": "ci-handoff-intent",
            },
        ],
        "edges": [{"source": "t_ho", "target": "a_ho"}],
    }


def _graph_consent_then_marketing_text() -> dict:
    return {
        "nodes": [
            {"id": "t_cp", "kind": "trigger"},
            {
                "id": "p_prefs",
                "kind": "action",
                "action_type": "update_preferences",
                "marketing_opt_in": True,
                "transactional_allowed": True,
                "disclosure_copy_slug": "flow-consent-ci",
            },
            {
                "id": "a_mkt",
                "kind": "action",
                "action_type": "send_text",
                "text_body": "promo after consent node",
                "preference_kind": "marketing",
            },
        ],
        "edges": [
            {"source": "t_cp", "target": "p_prefs"},
            {"source": "p_prefs", "target": "a_mkt"},
        ],
    }


def _graph_marketing_send_only() -> dict:
    """Marketing apos update_preferences (regra 6.3). Opt-in false -> bloqueado."""
    return {
        "nodes": [
            {"id": "t_mk", "kind": "trigger"},
            {
                "id": "p0",
                "kind": "action",
                "action_type": "update_preferences",
                "marketing_opt_in": False,
                "transactional_allowed": True,
                "disclosure_copy_slug": "baseline-v1",
            },
            {
                "id": "a_mk",
                "kind": "action",
                "action_type": "send_text",
                "text_body": "marketing without opt-in path",
                "preference_kind": "marketing",
            },
        ],
        "edges": [
            {"source": "t_mk", "target": "p0"},
            {"source": "p0", "target": "a_mk"},
        ],
    }


def _insert_waba_phone(
    admin: str,
    *,
    phone_number_id: str,
    environment: str,
    tenant: str = TENANT,
    waba_id: str = "ci-atdd-waba",
) -> None:
    wpn_row = str(uuid.uuid4())
    with psycopg.connect(admin) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO waba_phone_numbers
                  (id, tenant_id, waba_id, phone_number_id, display_phone_number,
                   environment, status)
                VALUES (%s::uuid, %s::uuid, %s, %s, %s, %s, 'active')
                ON CONFLICT ON CONSTRAINT uq_waba_phone_tenant_phone_env DO NOTHING
                """,
                (
                    wpn_row,
                    tenant,
                    waba_id,
                    phone_number_id,
                    "+15550003333",
                    environment,
                ),
            )
        conn.commit()


def _create_publish_flow(
    client: TestClient,
    definition: dict,
    *,
    publish_env: str,
) -> str:
    r = client.post(
        "/v1/me/flows",
        headers=_HDR_OP,
        json={"name": f"engine-e2e-{time.time_ns()}", "definition": definition},
    )
    assert r.status_code == 201, r.text
    fid = r.json()["id"]
    rs = client.post(
        f"/v1/me/flows/{fid}/sandbox-run",
        headers=_HDR_OP,
        params={"environment": "sandbox"},
        json={"fixture_message": {"type": "text", "body": "hi"}},
    )
    assert rs.status_code == 200, rs.text
    rp = client.post(
        f"/v1/me/flows/{fid}/publish",
        headers=_HDR_OP,
        json={"environment": publish_env},
    )
    assert rp.status_code == 200, rp.text
    return fid


def _webhook_payload(
    *,
    uid: str,
    ts: str,
    phone_number_id: str,
    waba_id: str = "ci-atdd-waba",
    from_num: str = "15550009999",
) -> dict:
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": waba_id,
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {"phone_number_id": phone_number_id},
                            "messages": [
                                {
                                    "id": uid,
                                    "from": from_num,
                                    "timestamp": ts,
                                    "type": "text",
                                    "text": {"body": "trigger"},
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }


def _post_whatsapp_webhook(client: TestClient, payload: dict, secret: str):
    body = json.dumps(payload).encode("utf-8")
    return client.post(
        "/v1/webhooks/whatsapp",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": _sign(body, secret),
        },
    )


@pytest.mark.integration
def test_staging_webhook_triggers_engine_outbound(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENBSP_FLOW_ENGINE_ENABLED", "true")
    monkeypatch.setenv("OPENBSP_FLOW_ENGINE_ENVIRONMENTS", "staging")
    monkeypatch.setenv("WHATSAPP_WEBHOOK_APP_SECRET", "ingress-secret")

    from app.core.config import get_settings

    get_settings.cache_clear()

    admin = os.environ["ALEMBIC_SYNC_URL"]
    staging_phone = f"ci-engine-staging-{uuid.uuid4().hex[:8]}"
    _insert_waba_phone(admin, phone_number_id=staging_phone, environment="staging")

    _create_publish_flow(client, _graph_send_text(), publish_env="staging")

    uid = f"wamid.eng-{time.time_ns()}"
    ts = str(int(time.time()))
    wh = _post_whatsapp_webhook(
        client,
        _webhook_payload(uid=uid, ts=ts, phone_number_id=staging_phone),
        "ingress-secret",
    )
    assert wh.status_code == 202, wh.text

    pat = f"engine:{uid}%"
    with psycopg.connect(admin) as conn:
        with conn.cursor() as cur:
            cur.execute(
                (
                    "SELECT 1 FROM outbound_whatsapp_messages "
                    "WHERE tenant_id = %s::uuid AND idempotency_key LIKE %s"
                ),
                (TENANT, pat),
            )
            row = cur.fetchone()
    assert row is not None


@pytest.mark.integration
def test_duplicate_webhook_does_not_enqueue_second_outbound(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENBSP_FLOW_ENGINE_ENABLED", "true")
    monkeypatch.setenv("OPENBSP_FLOW_ENGINE_ENVIRONMENTS", "staging")
    monkeypatch.setenv("WHATSAPP_WEBHOOK_APP_SECRET", "ingress-secret")

    from app.core.config import get_settings

    get_settings.cache_clear()

    admin = os.environ["ALEMBIC_SYNC_URL"]
    staging_phone = f"ci-engine-dup-{uuid.uuid4().hex[:8]}"
    _insert_waba_phone(admin, phone_number_id=staging_phone, environment="staging")
    _create_publish_flow(client, _graph_send_text(), publish_env="staging")

    uid = f"wamid.dup-{time.time_ns()}"
    ts = str(int(time.time()))
    payload = _webhook_payload(uid=uid, ts=ts, phone_number_id=staging_phone)

    wh1 = _post_whatsapp_webhook(client, payload, "ingress-secret")
    assert wh1.status_code == 202, wh1.text
    b1 = wh1.json()
    assert b1.get("enqueued", 0) >= 1
    pat = f"engine:{uid}%"
    with psycopg.connect(admin) as conn:
        with conn.cursor() as cur:
            cur.execute(
                (
                    "SELECT count(*) FROM outbound_whatsapp_messages "
                    "WHERE tenant_id = %s::uuid AND idempotency_key LIKE %s"
                ),
                (TENANT, pat),
            )
            n1 = cur.fetchone()[0]

    wh2 = _post_whatsapp_webhook(client, payload, "ingress-secret")
    assert wh2.status_code == 202, wh2.text
    assert wh2.json().get("deduplicated", 0) >= 1

    with psycopg.connect(admin) as conn:
        with conn.cursor() as cur:
            cur.execute(
                (
                    "SELECT count(*) FROM outbound_whatsapp_messages "
                    "WHERE tenant_id = %s::uuid AND idempotency_key LIKE %s"
                ),
                (TENANT, pat),
            )
            n2 = cur.fetchone()[0]
    assert n2 == n1 == 1


@pytest.mark.integration
def test_engine_apply_tag_links_conversation(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENBSP_FLOW_ENGINE_ENABLED", "true")
    monkeypatch.setenv("OPENBSP_FLOW_ENGINE_ENVIRONMENTS", "staging")
    monkeypatch.setenv("WHATSAPP_WEBHOOK_APP_SECRET", "ingress-secret")

    from app.core.config import get_settings

    get_settings.cache_clear()

    admin = os.environ["ALEMBIC_SYNC_URL"]
    phone = f"ci-engine-tag-{uuid.uuid4().hex[:8]}"
    _insert_waba_phone(admin, phone_number_id=phone, environment="staging")
    tname = f"engine-ci-{uuid.uuid4().hex[:6]}"
    _create_publish_flow(client, _graph_apply_tag(tname), publish_env="staging")

    uid = f"wamid.tag-{time.time_ns()}"
    wh = _post_whatsapp_webhook(
        client,
        _webhook_payload(uid=uid, ts=str(int(time.time())), phone_number_id=phone),
        "ingress-secret",
    )
    assert wh.status_code == 202, wh.text

    conv_id = derived_conversation_id(UUID(TENANT), "ci-atdd-waba", "15550009999")
    with psycopg.connect(admin) as conn:
        with conn.cursor() as cur:
            cur.execute(
                (
                    "SELECT 1 FROM inbox_conversation_tags ict "
                    "JOIN inbox_tags it ON it.id = ict.tag_id "
                    "WHERE ict.conversation_id = %s AND it.name = %s "
                    "AND ict.tenant_id = %s::uuid"
                ),
                (conv_id, tname, TENANT),
            )
            assert cur.fetchone() is not None


@pytest.mark.integration
def test_engine_handoff_queued_on_conversation(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENBSP_FLOW_ENGINE_ENABLED", "true")
    monkeypatch.setenv("OPENBSP_FLOW_ENGINE_ENVIRONMENTS", "staging")
    monkeypatch.setenv("WHATSAPP_WEBHOOK_APP_SECRET", "ingress-secret")

    from app.core.config import get_settings

    get_settings.cache_clear()

    admin = os.environ["ALEMBIC_SYNC_URL"]
    phone = f"ci-engine-ho-{uuid.uuid4().hex[:8]}"
    _insert_waba_phone(admin, phone_number_id=phone, environment="staging")
    _create_publish_flow(client, _graph_handoff(), publish_env="staging")

    uid = f"wamid.ho-{time.time_ns()}"
    contact = "15550008777"
    wh = _post_whatsapp_webhook(
        client,
        _webhook_payload(
            uid=uid,
            ts=str(int(time.time())),
            phone_number_id=phone,
            from_num=contact,
        ),
        "ingress-secret",
    )
    assert wh.status_code == 202, wh.text

    conv_id = derived_conversation_id(UUID(TENANT), "ci-atdd-waba", contact)

    with psycopg.connect(admin) as conn:
        with conn.cursor() as cur:
            cur.execute(
                (
                    "SELECT handoff_state, intent_summary "
                    "FROM inbox_conversation_handoffs "
                    "WHERE conversation_id = %s AND tenant_id = %s::uuid"
                ),
                (conv_id, TENANT),
            )
            row = cur.fetchone()
    assert row is not None
    assert row[0] == "queued"
    assert row[1] == "ci-handoff-intent"


@pytest.mark.integration
def test_engine_skips_when_line_environment_not_allowlisted(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Linha em `development`; allowlist so `staging` ? motor nao corre (FR26 gate)."""
    monkeypatch.setenv("OPENBSP_FLOW_ENGINE_ENABLED", "true")
    monkeypatch.setenv("OPENBSP_FLOW_ENGINE_ENVIRONMENTS", "staging")
    monkeypatch.setenv("WHATSAPP_WEBHOOK_APP_SECRET", "ingress-secret")

    from app.core.config import get_settings

    get_settings.cache_clear()

    admin = os.environ["ALEMBIC_SYNC_URL"]
    dev_phone = f"ci-engine-devonly-{uuid.uuid4().hex[:8]}"
    _insert_waba_phone(admin, phone_number_id=dev_phone, environment="development")
    _create_publish_flow(client, _graph_send_text(), publish_env="development")

    uid = f"wamid.skip-{time.time_ns()}"
    wh = _post_whatsapp_webhook(
        client,
        _webhook_payload(uid=uid, ts=str(int(time.time())), phone_number_id=dev_phone),
        "ingress-secret",
    )
    assert wh.status_code == 202, wh.text

    pat = f"engine:{uid}%"
    with psycopg.connect(admin) as conn:
        with conn.cursor() as cur:
            cur.execute(
                (
                    "SELECT 1 FROM outbound_whatsapp_messages "
                    "WHERE tenant_id = %s::uuid AND idempotency_key LIKE %s"
                ),
                (TENANT, pat),
            )
            assert cur.fetchone() is None


@pytest.mark.integration
def test_engine_update_preferences_unblocks_marketing_send(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENBSP_FLOW_ENGINE_ENABLED", "true")
    monkeypatch.setenv("OPENBSP_FLOW_ENGINE_ENVIRONMENTS", "staging")
    monkeypatch.setenv("WHATSAPP_WEBHOOK_APP_SECRET", "ingress-secret")

    from app.core.config import get_settings

    get_settings.cache_clear()

    admin = os.environ["ALEMBIC_SYNC_URL"]
    phone = f"ci-engine-pref-{uuid.uuid4().hex[:8]}"
    _insert_waba_phone(admin, phone_number_id=phone, environment="staging")
    _create_publish_flow(
        client,
        _graph_consent_then_marketing_text(),
        publish_env="staging",
    )

    contact = f"15579{uuid.uuid4().int % 10**7:07d}"
    uid = f"wamid.prefs-{time.time_ns()}"
    wh = _post_whatsapp_webhook(
        client,
        _webhook_payload(
            uid=uid,
            ts=str(int(time.time())),
            phone_number_id=phone,
            from_num=contact,
        ),
        "ingress-secret",
    )
    assert wh.status_code == 202, wh.text

    pat = f"engine:{uid}%"
    with psycopg.connect(admin) as conn:
        with conn.cursor() as cur:
            cur.execute(
                (
                    "SELECT 1 FROM outbound_whatsapp_messages "
                    "WHERE tenant_id = %s::uuid AND idempotency_key LIKE %s"
                ),
                (TENANT, pat),
            )
            assert cur.fetchone() is not None
            cur.execute(
                (
                    "SELECT marketing_opt_in, disclosure_copy_slug "
                    "FROM tenant_contact_preferences "
                    "WHERE tenant_id = %s::uuid AND contact_id = %s"
                ),
                (TENANT, contact),
            )
            pr = cur.fetchone()
    assert pr is not None
    assert pr[0] is True
    assert pr[1] == "flow-consent-ci"


@pytest.mark.integration
def test_engine_blocks_marketing_send_without_opt_in_row(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENBSP_FLOW_ENGINE_ENABLED", "true")
    monkeypatch.setenv("OPENBSP_FLOW_ENGINE_ENVIRONMENTS", "staging")
    monkeypatch.setenv("WHATSAPP_WEBHOOK_APP_SECRET", "ingress-secret")

    from app.core.config import get_settings

    get_settings.cache_clear()

    admin = os.environ["ALEMBIC_SYNC_URL"]
    phone = f"ci-engine-mblk-{uuid.uuid4().hex[:8]}"
    _insert_waba_phone(admin, phone_number_id=phone, environment="staging")
    _create_publish_flow(
        client,
        _graph_marketing_send_only(),
        publish_env="staging",
    )

    contact = f"15578{uuid.uuid4().int % 10**7:07d}"
    uid = f"wamid.mblk-{time.time_ns()}"
    wh = _post_whatsapp_webhook(
        client,
        _webhook_payload(
            uid=uid,
            ts=str(int(time.time())),
            phone_number_id=phone,
            from_num=contact,
        ),
        "ingress-secret",
    )
    assert wh.status_code == 202, wh.text

    pat = f"engine:{uid}%"
    with psycopg.connect(admin) as conn:
        with conn.cursor() as cur:
            cur.execute(
                (
                    "SELECT 1 FROM outbound_whatsapp_messages "
                    "WHERE tenant_id = %s::uuid AND idempotency_key LIKE %s"
                ),
                (TENANT, pat),
            )
            assert cur.fetchone() is None

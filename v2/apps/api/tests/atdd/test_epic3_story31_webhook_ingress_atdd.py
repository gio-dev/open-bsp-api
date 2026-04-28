"""ATDD Story 3.1 - Webhook entrada, verificacao Meta, encaminhamento (RED until DS)."""

import hashlib
import hmac
import json
import os
import time

import pytest
from app.core.config import get_settings
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.atdd, pytest.mark.epic3_atdd]


def _sign(body: bytes, secret: str) -> str:
    return (
        "sha256=" + hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    )


@pytest.mark.atdd
def test_story_31_webhook_meta_verification_get(client: TestClient):
    """3.1: GET hub challenge (Meta webhook verification)."""
    r = client.get(
        "/v1/webhooks/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "atdd-verify",
            "hub.challenge": "challengestring",
        },
    )
    assert r.status_code == 200, r.text


@pytest.mark.atdd
def test_story_31_webhook_post_accepts_valid_signature_stub(client: TestClient):
    """3.1: POST aceite; com APP_SECRET valida HMAC.

    Sem APP_SECRET em dev stub, assinatura nao e validada (header ignorado).
    """
    get_settings.cache_clear()
    payload = {"object": "whatsapp_business_account", "entry": []}
    body = json.dumps(payload).encode("utf-8")
    secret = os.environ.get("WHATSAPP_WEBHOOK_APP_SECRET")
    headers = {"Content-Type": "application/json"}
    if secret:
        headers["X-Hub-Signature-256"] = _sign(body, secret)
    else:
        headers["X-Hub-Signature-256"] = "sha256=00"
    r = client.post("/v1/webhooks/whatsapp", content=body, headers=headers)
    assert r.status_code in (200, 202), r.text
    data = r.json()
    assert data.get("status") == "accepted"
    assert data.get("request_id")


@pytest.mark.atdd
@pytest.mark.skipif(
    not os.getenv("DATABASE_URL"),
    reason="enfileiramento exige DATABASE_URL (CI api-ci)",
)
def test_story_31_webhook_post_enqueues_ci_waba(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """3.1: com BD + WABA seed, uma mensagem gera enqueued >= 1."""
    monkeypatch.setenv("WHATSAPP_WEBHOOK_APP_SECRET", "atdd-ci-waba-secret")
    get_settings.cache_clear()
    uid = f"wamid.atdd-{os.getpid()}-{time.time_ns()}"
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
                                    "timestamp": str(int(time.time())),
                                    "type": "text",
                                    "text": {"body": "atdd"},
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
            "X-Hub-Signature-256": _sign(body, "atdd-ci-waba-secret"),
        },
    )
    assert r.status_code == 202, r.text
    assert r.json()["enqueued"] >= 1
    get_settings.cache_clear()

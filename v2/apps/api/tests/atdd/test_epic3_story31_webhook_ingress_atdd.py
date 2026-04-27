"""ATDD Story 3.1 - Webhook entrada, verificacao Meta, encaminhamento (RED until DS)."""

import hashlib
import hmac
import json
import os

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
    """3.1: POST aceite; HMAC real se APP_SECRET no env, senao stub sha256=00."""
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

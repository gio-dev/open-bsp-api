"""Webhook HMAC quando WHATSAPP_WEBHOOK_APP_SECRET esta definido."""

import hashlib
import hmac
import json

import pytest
from app.core.config import get_settings
from app.main import app
from fastapi.testclient import TestClient


def _sign(body: bytes, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


@pytest.fixture
def client_no_lru() -> TestClient:
    with TestClient(app) as c:
        yield c


def test_post_rejects_bad_signature_when_secret_configured(
    client_no_lru: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("WHATSAPP_WEBHOOK_APP_SECRET", "unit-test-secret")
    get_settings.cache_clear()
    body = json.dumps({"object": "whatsapp_business_account", "entry": []}).encode(
        "utf-8"
    )
    r = client_no_lru.post(
        "/v1/webhooks/whatsapp",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": "sha256=00",
        },
    )
    assert r.status_code == 401
    get_settings.cache_clear()
    monkeypatch.delenv("WHATSAPP_WEBHOOK_APP_SECRET", raising=False)


def test_post_accepts_valid_signature_when_secret_configured(
    client_no_lru: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    secret = "unit-test-secret-2"
    monkeypatch.setenv("WHATSAPP_WEBHOOK_APP_SECRET", secret)
    get_settings.cache_clear()
    body = json.dumps({"object": "whatsapp_business_account", "entry": []}).encode(
        "utf-8"
    )
    r = client_no_lru.post(
        "/v1/webhooks/whatsapp",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": _sign(body, secret),
        },
    )
    assert r.status_code == 202, r.text
    get_settings.cache_clear()
    monkeypatch.delenv("WHATSAPP_WEBHOOK_APP_SECRET", raising=False)


def test_post_rejects_body_over_configured_limit(
    client_no_lru: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("WHATSAPP_WEBHOOK_MAX_BODY_BYTES", "64")
    get_settings.cache_clear()
    body = b"x" * 65
    r = client_no_lru.post(
        "/v1/webhooks/whatsapp",
        content=body,
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 413
    get_settings.cache_clear()
    monkeypatch.delenv("WHATSAPP_WEBHOOK_MAX_BODY_BYTES", raising=False)


def test_post_requires_app_secret_when_not_dev_stub(
    client_no_lru: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("AUTH_DEV_STUB", "false")
    monkeypatch.delenv("WHATSAPP_WEBHOOK_APP_SECRET", raising=False)
    get_settings.cache_clear()
    body = json.dumps({"object": "whatsapp_business_account", "entry": []}).encode(
        "utf-8"
    )
    r = client_no_lru.post(
        "/v1/webhooks/whatsapp",
        content=body,
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 503, r.text
    get_settings.cache_clear()
    monkeypatch.setenv("AUTH_DEV_STUB", "true")
    get_settings.cache_clear()

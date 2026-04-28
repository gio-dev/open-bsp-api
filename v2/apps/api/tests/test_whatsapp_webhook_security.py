"""Webhook HMAC quando WHATSAPP_WEBHOOK_APP_SECRET esta definido."""

import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta

import pytest
from app.core.config import get_settings
from app.main import app
from app.whatsapp.webhook_ingress import (
    ensure_fresh_event,
    meta_unix_ts,
    payload_has_queueable_items,
)
from fastapi import HTTPException
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


def test_meta_unix_ts() -> None:
    assert meta_unix_ts("1234567890") == datetime(2009, 2, 13, 23, 31, 30, tzinfo=UTC)
    assert meta_unix_ts(1234567890) == datetime(2009, 2, 13, 23, 31, 30, tzinfo=UTC)
    assert meta_unix_ts(None) is None
    assert meta_unix_ts("nope") is None


def test_payload_has_queueable_items() -> None:
    assert not payload_has_queueable_items({"entry": []})
    pl = {
        "entry": [
            {
                "id": "waba1",
                "changes": [
                    {
                        "value": {
                            "messages": [{"id": " mid ", "timestamp": "1"}],
                        }
                    }
                ],
            }
        ]
    }
    assert payload_has_queueable_items(pl)
    assert not payload_has_queueable_items(
        {"entry": [{"id": "waba1", "changes": [{"value": {}}]}]}
    )


def test_ensure_fresh_event_rejects_stale() -> None:
    old = datetime.now(UTC) - timedelta(hours=1)
    with pytest.raises(HTTPException) as ei:
        ensure_fresh_event(
            old,
            max_age_seconds=60,
            request_id="rid",
            waba_id="w1",
            source_id="s1",
        )
    assert ei.value.status_code == 409


def test_ensure_fresh_event_skips_when_no_ts() -> None:
    ensure_fresh_event(
        None,
        max_age_seconds=60,
        request_id="rid",
        waba_id="w1",
        source_id="s1",
    )

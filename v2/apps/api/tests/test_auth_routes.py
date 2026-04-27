"""Rotas /v1/auth/* sem Postgres (Story 2.1)."""

import time

import pytest
from app.auth.session_cookie import encode_payload
from app.core.config import get_settings
from fastapi.testclient import TestClient


def test_auth_session_without_cookie_returns_401(client: TestClient) -> None:
    r = client.get("/v1/auth/session")
    assert r.status_code == 401
    body = r.json()
    assert body.get("code") == "http_401"


def test_oidc_login_without_idp_config_returns_503(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("OIDC_ISSUER", raising=False)
    monkeypatch.delenv("OIDC_CLIENT_ID", raising=False)
    monkeypatch.delenv("OIDC_REDIRECT_URI", raising=False)
    get_settings.cache_clear()
    r = client.get("/v1/auth/oidc/login")
    assert r.status_code == 503


def test_auth_logout_returns_json(client: TestClient) -> None:
    r = client.post("/v1/auth/logout")
    assert r.status_code == 200
    assert r.json().get("status") == "logged_out"


def test_auth_session_no_secret_returns_503(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("SESSION_SIGNING_SECRET", raising=False)
    get_settings.cache_clear()
    r = client.get("/v1/auth/session")
    assert r.status_code == 503
    assert r.json().get("code")
    monkeypatch.setenv("SESSION_SIGNING_SECRET", "test-session-secret-atdd")
    get_settings.cache_clear()


def test_auth_session_rejects_only_unknown_roles_in_cookie(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Papeis no cookie sao filtrados; so desconhecidos => 401."""
    settings = get_settings()
    secret = settings.session_signing_secret or "test-session-secret-atdd"
    now = int(time.time())
    tok = encode_payload(
        {
            "v": 1,
            "uid": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            "tid": "11111111-1111-4111-8111-111111111111",
            "roles": ["not_a_valid_tenant_role"],
            "exp": now + 3600,
        },
        secret,
    )
    r = client.get(
        "/v1/auth/session",
        cookies={settings.session_cookie_name: tok},
    )
    assert r.status_code == 401

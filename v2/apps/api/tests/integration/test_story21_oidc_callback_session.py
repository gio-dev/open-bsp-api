"""Story 2.1: callback OIDC cria cookie de sessao (Postgres + seed)."""

from __future__ import annotations

import os
import time

import pytest
from app.auth.session_cookie import encode_payload
from app.core.config import get_settings
from fastapi.testclient import TestClient

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL"),
    reason="needs DATABASE_URL (CI postgres)",
)


@pytest.mark.integration
def test_oidc_callback_sets_session_cookie(
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> None:
    import app.api.routes.auth_oidc as auth_oidc

    monkeypatch.setenv("OIDC_ISSUER", "http://fake-idp.test")
    monkeypatch.setenv("OIDC_CLIENT_ID", "atdd-client")
    monkeypatch.setenv(
        "OIDC_REDIRECT_URI",
        "http://localhost:5173/v1/auth/oidc/callback",
    )
    monkeypatch.setenv("SESSION_COOKIE_SECURE", "false")
    get_settings.cache_clear()

    async def _fake_meta(_issuer: str) -> dict:
        return {
            "authorization_endpoint": "http://fake-idp.test/authorize",
            "token_endpoint": "http://fake-idp.test/token",
            "jwks_uri": "http://fake-idp.test/jwks",
            "issuer": "http://fake-idp.test",
        }

    async def _fake_exchange(*_a: object, **_kw: object) -> dict:
        return {"id_token": "header.payload.sig"}

    def _fake_verify(*_a: object, **_kw: object) -> dict:
        return {"sub": "ci-atdd-sub", "email": "seeded@local"}

    monkeypatch.setattr(auth_oidc, "fetch_oidc_metadata", _fake_meta)
    monkeypatch.setattr(auth_oidc, "exchange_authorization_code", _fake_exchange)
    monkeypatch.setattr(auth_oidc, "verify_id_token", _fake_verify)

    secret = os.environ.get("SESSION_SIGNING_SECRET", "test-session-secret-atdd")
    state = "csrf-state-test"
    hs = encode_payload(
        {
            "v": 1,
            "state": state,
            "cv": "pkce-verifier",
            "exp": int(time.time()) + 300,
        },
        secret,
    )

    client.cookies.clear()
    client.cookies.set("obsp_oidc", hs)
    r = client.get(
        "/v1/auth/oidc/callback",
        params={"code": "auth-code", "state": state},
        follow_redirects=False,
    )
    assert r.status_code == 302
    set_cookie = r.headers.get("set-cookie") or ""
    assert "obsp_session" in set_cookie.lower()
    s = client.get("/v1/auth/session")
    assert s.status_code == 200
    body = s.json()
    assert body.get("email") == "seeded@local"
    assert body.get("tenant_id") == "11111111-1111-4111-8111-111111111111"

    client.cookies.clear()
    get_settings.cache_clear()

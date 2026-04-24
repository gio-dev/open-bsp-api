"""Rotas /v1/auth/* sem Postgres (Story 2.1)."""

from fastapi.testclient import TestClient


def test_auth_session_without_cookie_returns_401(client: TestClient) -> None:
    r = client.get("/v1/auth/session")
    assert r.status_code == 401
    body = r.json()
    assert body.get("code") == "http_401"


def test_oidc_login_without_idp_config_returns_503(client: TestClient) -> None:
    r = client.get("/v1/auth/oidc/login")
    assert r.status_code == 503


def test_auth_logout_returns_json(client: TestClient) -> None:
    r = client.post("/v1/auth/logout")
    assert r.status_code == 200
    assert r.json().get("status") == "logged_out"

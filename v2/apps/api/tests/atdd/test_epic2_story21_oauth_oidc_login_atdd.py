"""ATDD Story 2.1 - OAuth/OIDC login base consola (RED until DS)."""

import pytest
from fastapi.testclient import TestClient


def _openapi_paths(client: TestClient) -> dict:
    r = client.get("/openapi.json")
    assert r.status_code == 200
    return r.json().get("paths", {})


@pytest.mark.atdd
def test_story_21_openapi_includes_oauth_session_routes(client: TestClient):
    """2.1: consola OAuth/OIDC - rotas auth concretas sob /v1 (CDA)."""
    paths = _openapi_paths(client)
    assert "/v1/auth/oidc/login" in paths, "GET login OIDC documentado"
    assert "/v1/auth/oidc/callback" in paths, "GET callback OIDC documentado"
    assert "/v1/auth/session" in paths, "GET session documentada"
    assert "/v1/auth/logout" in paths, "POST logout documentada"

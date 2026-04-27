"""ATDD Story 2.4 - Webhook verification secret rotation."""

import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.atdd, pytest.mark.epic2_atdd]


def _paths(client: TestClient) -> dict:
    r = client.get("/openapi.json")
    assert r.status_code == 200
    return r.json().get("paths", {})


def test_story_24_openapi_webhook_secrets(client: TestClient) -> None:
    """2.4: listagem e rotacao documentadas em OpenAPI."""
    p = _paths(client)
    assert "/v1/me/webhook-secrets" in p
    assert "get" in p["/v1/me/webhook-secrets"]
    assert "/v1/me/webhook-secrets/rotate" in p
    assert "post" in p["/v1/me/webhook-secrets/rotate"]


def test_story_24_webhook_secret_rotation_endpoint(client: TestClient) -> None:
    """2.4: rotate webhook verification secret; 201 e verify_token (uma vez)."""
    r = client.post(
        "/v1/me/webhook-secrets/rotate",
        headers={
            "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
            "X-Dev-User-Id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            "X-Dev-Roles": "org_admin",
        },
        json={},
    )
    if r.status_code == 503:
        pytest.skip("database not configured in this runner")
    assert r.status_code == 201, r.text
    data = r.json()
    assert "verify_token" in data
    assert data["verify_token"].startswith("wvt_")

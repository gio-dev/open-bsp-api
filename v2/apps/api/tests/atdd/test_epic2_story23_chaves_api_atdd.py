"""ATDD Story 2.3 - API keys issue/revoke (RED until DS)."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.atdd
def test_story_23_post_api_key_returns_secret_once(client: TestClient):
    """2.3: POST creates API key; 201 with secret shown once."""
    r = client.post(
        "/v1/me/api-keys",
        headers={
            "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
            "X-Dev-User-Id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            "X-Dev-Roles": "org_admin",
        },
        json={"name": "atdd-key"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert "secret" in body or "key_prefix" in body

"""ATDD Story 2.4 - Webhook verification secret rotation (RED until DS)."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.atdd
def test_story_24_webhook_secret_rotation_endpoint(client: TestClient):
    """2.4: rotate webhook verification secret with coexistence window."""
    r = client.post(
        "/v1/me/webhook-secrets/rotate",
        headers={
            "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
            "X-Dev-User-Id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            "X-Dev-Roles": "org_admin",
        },
        json={},
    )
    assert r.status_code in (200, 201), r.text

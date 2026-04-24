"""ATDD Story 8.3 - Entitlements e alertas (RED until DS)."""

import pytest
from fastapi.testclient import TestClient

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "org_admin",
}


@pytest.mark.atdd
def test_story_83_entitlements_threshold(client: TestClient):
    """8.3: entitlements and thresholds."""
    r = client.get("/v1/me/entitlements", headers=_HDR)
    assert r.status_code == 200, r.text

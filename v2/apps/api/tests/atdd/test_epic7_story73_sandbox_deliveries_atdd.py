"""ATDD Story 7.3 - Sandbox tenant-scoped e entregas (RED until DS)."""

import pytest
from fastapi.testclient import TestClient

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "org_admin",
}


@pytest.mark.atdd
def test_story_73_sandbox_webhook_deliveries_list(client: TestClient):
    """7.3: sandbox webhook delivery history (tenant-scoped)."""
    r = client.get("/v1/me/sandbox/webhook-deliveries", headers=_HDR)
    assert r.status_code == 200, r.text

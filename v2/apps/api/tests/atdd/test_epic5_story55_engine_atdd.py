"""ATDD Story 5.5 - Engine aplica acoes (RED until DS)."""

import pytest
from fastapi.testclient import TestClient

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "org_admin",
}


@pytest.mark.atdd
def test_story_55_engine_status_probe(client: TestClient):
    """5.5: engine enabled / health for tenant (adjust to DS)."""
    r = client.get("/v1/me/engine/status", headers=_HDR)
    assert r.status_code == 200, r.text

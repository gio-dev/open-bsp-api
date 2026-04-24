"""ATDD Story 9.4 - Retencao e aplicacao (RED until DS)."""

import pytest
from fastapi.testclient import TestClient

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "org_admin",
}


@pytest.mark.atdd
def test_story_94_retention_policies(client: TestClient):
    """9.4: retention policies config."""
    r = client.get("/v1/me/governance/retention", headers=_HDR)
    assert r.status_code == 200, r.text

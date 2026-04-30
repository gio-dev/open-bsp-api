"""ATDD Story 5.4 - Versao e audit de materialidade (RED until DS)."""

import pytest
from fastapi.testclient import TestClient

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "org_admin",
}


@pytest.mark.atdd
@pytest.mark.epic5_atdd
def test_story_54_flow_versions_list(client: TestClient):
    """5.4: append-only version history for a flow."""
    r = client.get(
        "/v1/me/flows/atdd-flow/versions",
        headers=_HDR,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert isinstance(data.get("items"), list)
    assert "total" in data
    assert isinstance(data["total"], int)

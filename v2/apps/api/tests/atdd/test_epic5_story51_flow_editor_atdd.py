"""ATDD Story 5.1 - Editor de fluxos e validacao (RED until DS)."""

import pytest
from fastapi.testclient import TestClient

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "org_admin",
}


@pytest.mark.atdd
@pytest.mark.epic5_atdd
def test_story_51_flow_validate_endpoint(client: TestClient):
    """5.1: validate rule flow draft (field/line errors)."""
    r = client.post(
        "/v1/me/flows/validate",
        headers=_HDR,
        json={"nodes": [], "edges": []},
    )
    assert r.status_code in (200, 422), r.text

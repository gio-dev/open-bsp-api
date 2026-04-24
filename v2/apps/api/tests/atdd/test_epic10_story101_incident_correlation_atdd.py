"""ATDD Story 10.1 - Correlacao e culpa (RED until DS)."""

import pytest
from fastapi.testclient import TestClient

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "support_n2",
}


@pytest.mark.atdd
def test_story_101_support_incident_search(client: TestClient):
    """10.1: incident search by request_id (N2)."""
    r = client.get(
        "/v1/internal/support/incidents",
        headers=_HDR,
        params={"request_id": "atdd-req-1"},
    )
    assert r.status_code in (200, 403), r.text

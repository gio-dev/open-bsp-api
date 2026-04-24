"""ATDD Story 8.1 - Metering minimo (RED until DS)."""

import pytest
from fastapi.testclient import TestClient

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "org_admin",
}


@pytest.mark.atdd
def test_story_81_usage_events_aggregate(client: TestClient):
    """8.1: aggregated usage events / summary."""
    r = client.get("/v1/me/usage/summary", headers=_HDR)
    assert r.status_code == 200, r.text

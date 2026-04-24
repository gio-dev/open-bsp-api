"""ATDD Story 8.4 - Export uso e faturacao (RED until DS)."""

import pytest
from fastapi.testclient import TestClient

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "finance",
}


@pytest.mark.atdd
def test_story_84_usage_csv_export(client: TestClient):
    """8.4: CSV usage export (finance or 403)."""
    r = client.get("/v1/me/usage/export.csv", headers=_HDR)
    assert r.status_code in (200, 403), r.text

"""ATDD Story 8.2 - Relatorios de valor anti-vanity (RED until DS)."""

import pytest
from fastapi.testclient import TestClient

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "finance",
}


@pytest.mark.atdd
def test_story_82_value_report_export(client: TestClient):
    """8.2: value report (finance role or 403)."""
    r = client.get("/v1/me/reports/value", headers=_HDR)
    assert r.status_code in (200, 403), r.text

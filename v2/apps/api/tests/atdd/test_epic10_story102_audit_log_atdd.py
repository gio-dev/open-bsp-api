"""ATDD Story 10.2 - Consulta audit log (RED until DS)."""

import pytest
from fastapi.testclient import TestClient

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "auditor",
}


@pytest.mark.atdd
def test_story_102_audit_log_query(client: TestClient):
    """10.2: filtered audit log query."""
    r = client.get("/v1/me/audit/events", headers=_HDR)
    assert r.status_code in (200, 403), r.text

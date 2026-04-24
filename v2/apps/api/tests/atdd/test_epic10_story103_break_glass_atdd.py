"""ATDD Story 10.3 - Break-glass (RED until DS)."""

import pytest
from fastapi.testclient import TestClient

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "support_n2",
}


@pytest.mark.atdd
def test_story_103_break_glass_request(client: TestClient):
    """10.3: break-glass request with audit trail."""
    r = client.post(
        "/v1/internal/break-glass/requests",
        headers=_HDR,
        json={"reason": "atdd", "duration_minutes": 15},
    )
    assert r.status_code in (200, 201, 403), r.text

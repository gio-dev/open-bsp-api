"""ATDD Story 4.4 - Sinais de atraso, falha e health (RED until DS)."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.atdd
def test_story_44_channel_health_endpoint(client: TestClient):
    """4.4: tenant-scoped channel health / incident signals."""
    r = client.get(
        "/v1/me/channel-health",
        headers={
            "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
            "X-Dev-Roles": "org_admin",
        },
    )
    assert r.status_code == 200, r.text

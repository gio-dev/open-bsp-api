"""ATDD Story 4.3 - Handoff e contexto minimo (RED until DS)."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.atdd
def test_story_43_handoff_state_visible(client: TestClient):
    """4.3: handoff summary / state for operator."""
    r = client.get(
        "/v1/me/conversations/atdd-conv-1/handoff",
        headers={
            "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
            "X-Dev-Roles": "org_admin",
        },
    )
    assert r.status_code == 200, r.text

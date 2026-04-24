"""ATDD Story 6.2 - Copy e estados bot/humano (RED until DS)."""

import pytest
from fastapi.testclient import TestClient

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "org_admin",
}


@pytest.mark.atdd
def test_story_62_conversation_mode_label(client: TestClient):
    """6.2: bot vs human mode visible for conversation."""
    r = client.get(
        "/v1/me/conversations/atdd-conv-1/mode",
        headers=_HDR,
    )
    assert r.status_code == 200, r.text

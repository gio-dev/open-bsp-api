"""ATDD Story 6.2 - Copy e estados bot/humano (RED until DS)."""

import pytest
from app.atdd_fixture_ids import ATDD_INBOX_CONVERSATION_ID
from fastapi.testclient import TestClient

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "org_admin",
}

pytestmark = [pytest.mark.atdd, pytest.mark.epic6_atdd]


def test_story_62_conversation_mode_label(client: TestClient):
    """6.2: bot vs human mode visible for conversation."""
    r = client.get(
        f"/v1/me/conversations/{ATDD_INBOX_CONVERSATION_ID}/mode",
        headers=_HDR,
        params={"environment": "sandbox"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["mode"] in ("bot_active", "human_active"), data
    assert "since" in data and data["since"]
    # Handoff seeded queued => human pipeline.
    assert data["mode"] == "human_active", data

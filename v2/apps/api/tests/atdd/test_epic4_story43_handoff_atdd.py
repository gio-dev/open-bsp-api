"""ATDD Story 4.3 - Handoff (RED until DS)."""

import pytest
from app.atdd_fixture_ids import ATDD_INBOX_CONVERSATION_ID
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.atdd, pytest.mark.epic4_atdd]

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "org_admin",
}


@pytest.mark.atdd
def test_story_43_get_conversation_handoff(client: TestClient):
    r = client.get(
        f"/v1/me/conversations/{ATDD_INBOX_CONVERSATION_ID}/handoff",
        headers=_HDR,
        params={"environment": "sandbox"},
    )
    assert r.status_code == 200, r.text

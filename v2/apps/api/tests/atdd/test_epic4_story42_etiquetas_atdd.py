"""ATDD Story 4.2 - Etiquetas inbox (RED until DS)."""

import pytest
from app.atdd_fixture_ids import ATDD_INBOX_CONVERSATION_ID
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.atdd, pytest.mark.epic4_atdd]

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "org_admin",
}

_ATDD_TAG_ID = "dddddddd-dddd-4ddd-8ddd-dddddddddddd"


@pytest.mark.atdd
def test_story_42_list_inbox_tags(client: TestClient):
    r = client.get("/v1/me/inbox/tags", headers=_HDR)
    assert r.status_code == 200, r.text


@pytest.mark.atdd
def test_story_42_patch_conversation_tags(client: TestClient):
    r = client.patch(
        f"/v1/me/conversations/{ATDD_INBOX_CONVERSATION_ID}/tags",
        headers=_HDR,
        params={"environment": "sandbox"},
        json={"tag_ids": [_ATDD_TAG_ID]},
    )
    assert r.status_code == 200, r.text

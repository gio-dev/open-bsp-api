"""ATDD Story 4.1 - Inbox split lista e thread (RED until DS)."""

import pytest
from fastapi.testclient import TestClient

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "org_admin",
}


@pytest.mark.atdd
def test_story_41_inbox_conversations_list(client: TestClient):
    """4.1: conversation list for inbox."""
    r = client.get("/v1/me/conversations", headers=_HDR)
    assert r.status_code == 200, r.text


@pytest.mark.atdd
def test_story_41_inbox_conversation_thread_messages(client: TestClient):
    """4.1: thread payload when a conversation is selected."""
    r = client.get("/v1/me/conversations/atdd-conv-1/messages", headers=_HDR)
    assert r.status_code == 200, r.text

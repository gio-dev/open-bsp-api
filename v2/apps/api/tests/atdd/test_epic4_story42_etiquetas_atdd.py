"""ATDD Story 4.2 - Etiquetas e triagem partilhada (RED until DS)."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.atdd
def test_story_42_conversation_tags_patch(client: TestClient):
    """4.2: add/remove shared tags on a conversation."""
    r = client.patch(
        "/v1/me/conversations/atdd-conv-1/tags",
        headers={
            "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
            "X-Dev-Roles": "org_admin",
        },
        json={"tag_ids": ["tag_1"]},
    )
    assert r.status_code in (200, 204), r.text

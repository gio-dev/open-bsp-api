"""Story 4.2: etiquetas partilhadas na inbox."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

TENANT = "11111111-1111-4111-8111-111111111111"
ATDD_TAG_ID = "dddddddd-dddd-4ddd-8ddd-dddddddddddd"

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL") or not os.getenv("ALEMBIC_SYNC_URL"),
    reason="needs DATABASE_URL and ALEMBIC_SYNC_URL (CI postgres)",
)


@pytest.mark.integration
def test_inbox_list_includes_shared_tags(client: TestClient) -> None:
    r = client.get(
        "/v1/me/conversations",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "operator",
        },
        params={"environment": "sandbox"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    conv = next(x for x in data["items"] if x["id"] == "atdd-conv-1")
    assert any(t["name"] == "atdd-label" for t in conv["tags"])


@pytest.mark.integration
def test_list_inbox_tags(client: TestClient) -> None:
    r = client.get(
        "/v1/me/inbox/tags",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "agent",
        },
    )
    assert r.status_code == 200, r.text
    names = {x["name"] for x in r.json()["items"]}
    assert "atdd-label" in names


@pytest.mark.integration
def test_patch_conversation_tags_idempotent(client: TestClient) -> None:
    r = client.patch(
        "/v1/me/conversations/atdd-conv-1/tags",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "operator",
        },
        params={"environment": "sandbox"},
        json={"tag_ids": [ATDD_TAG_ID]},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["conversation_id"] == "atdd-conv-1"
    assert {t["name"] for t in body["tags"]} == {"atdd-label"}


@pytest.mark.integration
def test_patch_conversation_tags_unknown_tag_422(client: TestClient) -> None:
    r = client.patch(
        "/v1/me/conversations/atdd-conv-1/tags",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "operator",
        },
        params={"environment": "sandbox"},
        json={"tag_ids": ["00000000-0000-4000-8000-000000000099"]},
    )
    assert r.status_code == 422, r.text
    assert "unknown" in r.json().get("message", "").lower()


@pytest.mark.integration
def test_patch_conversation_tags_viewer_forbidden(client: TestClient) -> None:
    r = client.patch(
        "/v1/me/conversations/atdd-conv-1/tags",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "viewer",
        },
        params={"environment": "sandbox"},
        json={"tag_ids": []},
    )
    assert r.status_code == 403, r.text

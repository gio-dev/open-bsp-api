"""ATDD Story 2.2 - RBAC / memberships per tenant (RED until DS)."""

import pytest
from fastapi.testclient import TestClient


def _openapi_paths(client: TestClient) -> dict:
    r = client.get("/openapi.json")
    assert r.status_code == 200
    return r.json().get("paths", {})


@pytest.mark.atdd
def test_story_22_openapi_includes_membership_or_roles(client: TestClient):
    """2.2: API de membros por tenant (paths concretos /v1/me/members)."""
    paths = _openapi_paths(client)
    assert "/v1/me/members" in paths, "GET /v1/me/members (lista de membros)"
    path_entry = paths["/v1/me/members"]
    assert "get" in path_entry, "GET list members"
    members_patch_key = next(
        (p for p in paths if p.startswith("/v1/me/members/") and "{" in p),
        None,
    )
    assert members_patch_key, "PATCH /v1/me/members/{user_id} documentado"
    assert "patch" in paths[members_patch_key], "PATCH member role"

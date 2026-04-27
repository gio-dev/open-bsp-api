"""Story 2.3: fluxo API keys com Postgres + RLS."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL") or not os.getenv("ALEMBIC_SYNC_URL"),
    reason="needs DATABASE_URL and ALEMBIC_SYNC_URL (CI postgres)",
)


@pytest.mark.integration
def test_create_list_no_secret_in_list_patch_revoke(client: TestClient) -> None:
    headers = {
        "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
        "X-Dev-Roles": "org_admin",
        "X-Dev-User-Id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
    }
    r_create = client.post(
        "/v1/me/api-keys",
        headers=headers,
        json={"name": "ci-integration-key"},
    )
    assert r_create.status_code == 201, r_create.text
    created = r_create.json()
    assert "secret" in created
    kid = created["id"]

    r_list = client.get("/v1/me/api-keys", headers=headers)
    assert r_list.status_code == 200
    items = r_list.json().get("items", [])
    match = next((i for i in items if i["id"] == kid), None)
    assert match is not None
    assert "secret" not in match

    r_patch = client.patch(
        f"/v1/me/api-keys/{kid}",
        headers=headers,
        json={"revoke_immediately": True},
    )
    assert r_patch.status_code == 200, r_patch.text
    assert r_patch.json().get("status") == "revoked"

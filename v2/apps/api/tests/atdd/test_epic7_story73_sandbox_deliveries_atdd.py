"""ATDD Story 7.3 - Sandbox tenant-scoped e entregas."""

import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.atdd, pytest.mark.epic7_atdd]

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "org_admin",
}

_ITEM_KEYS = frozenset(
    {
        "id",
        "request_id",
        "status",
        "enqueued",
        "deduplicated",
        "skipped",
        "created_at",
    },
)


@pytest.mark.atdd
def test_story_73_sandbox_webhook_deliveries_list(client: TestClient) -> None:
    """7.3: sandbox webhook delivery history (tenant-scoped)."""
    r = client.get("/v1/me/sandbox/webhook-deliveries", headers=_HDR)
    assert r.status_code == 200, r.text
    body = r.json()
    assert "items" in body
    assert isinstance(body["items"], list)
    for item in body["items"]:
        assert _ITEM_KEYS == set(item.keys()), item


@pytest.mark.atdd
def test_story_73_openapi_lists_webhook_deliveries_path(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()
    assert "/v1/me/sandbox/webhook-deliveries" in (spec.get("paths") or {})
    op = spec["paths"]["/v1/me/sandbox/webhook-deliveries"].get("get") or {}
    assert op.get("tags") == ["sandbox-webhooks"]


@pytest.mark.atdd
def test_story_73_operator_forbidden(client: TestClient) -> None:
    r = client.get(
        "/v1/me/sandbox/webhook-deliveries",
        headers={
            "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
            "X-Dev-Roles": "operator",
        },
    )
    assert r.status_code == 403, r.text

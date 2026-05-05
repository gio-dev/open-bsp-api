"""ATDD Story 8.1 - Metering minimo."""

import pytest
from app.db.models_usage import (
    USAGE_METRIC_INBOUND_MESSAGES,
    USAGE_METRIC_OUTBOUND_MESSAGES_ACCEPTED,
)
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.atdd, pytest.mark.epic8_atdd]

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "org_admin",
}

_TOP_KEYS = frozenset({"period_start", "period_end", "metrics"})
_METRIC_ITEM_KEYS = frozenset({"metric_key", "count"})


@pytest.mark.atdd
def test_story_81_usage_events_aggregate(client: TestClient) -> None:
    """8.1: aggregated usage events / summary."""
    r = client.get("/v1/me/usage/summary", headers=_HDR)
    assert r.status_code == 200, r.text
    body = r.json()
    assert _TOP_KEYS == set(body.keys()), body
    assert isinstance(body["metrics"], list)
    keys = {m["metric_key"] for m in body["metrics"]}
    assert keys == {
        USAGE_METRIC_INBOUND_MESSAGES,
        USAGE_METRIC_OUTBOUND_MESSAGES_ACCEPTED,
    }
    for m in body["metrics"]:
        assert _METRIC_ITEM_KEYS == set(m.keys()), m
        assert isinstance(m["count"], int) and m["count"] >= 0


@pytest.mark.atdd
def test_story_81_openapi_lists_usage_summary(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()
    assert "/v1/me/usage/summary" in (spec.get("paths") or {})
    op = spec["paths"]["/v1/me/usage/summary"].get("get") or {}
    assert op.get("tags") == ["usage"]


@pytest.mark.atdd
def test_story_81_operator_forbidden(client: TestClient) -> None:
    r = client.get(
        "/v1/me/usage/summary",
        headers={
            "X-Dev-Tenant-Id": _HDR["X-Dev-Tenant-Id"],
            "X-Dev-Roles": "operator",
        },
    )
    assert r.status_code == 403, r.text


@pytest.mark.atdd
def test_story_81_invalid_range_returns_400(client: TestClient) -> None:
    r = client.get(
        "/v1/me/usage/summary?since=2030-01-02&until=2030-01-01",
        headers=_HDR,
    )
    assert r.status_code == 400, r.text

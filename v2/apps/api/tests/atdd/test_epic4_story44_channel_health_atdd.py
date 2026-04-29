"""ATDD Story 4.4 ? GET /v1/me/channel-health (tenant, forma do payload)."""

import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.atdd, pytest.mark.epic4_atdd]


@pytest.mark.atdd
def test_story_44_channel_health_endpoint(client: TestClient):
    """4.4: resposta alinhada ao contrato e escopo tenant (stub dev)."""
    r = client.get(
        "/v1/me/channel-health",
        headers={
            "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
            "X-Dev-Roles": "org_admin",
        },
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert "healthy" in data
    assert isinstance(data["healthy"], bool)
    assert isinstance(data["incidents"], list)
    assert "counts" in data
    counts = data["counts"]
    for key in (
        "outbound_failed_meta",
        "outbound_failed_platform",
        "outbound_rate_limited",
        "outbound_stale_queued",
        "handoff_failed",
    ):
        assert key in counts
        assert isinstance(counts[key], int)
    for inc in data["incidents"]:
        assert inc["source"] in ("meta", "platform", "unknown")
        assert inc["severity"] in ("warning", "critical")
        assert "code" in inc and "summary" in inc and "next_step" in inc

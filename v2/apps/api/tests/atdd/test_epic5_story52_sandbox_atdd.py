"""ATDD Story 5.2 - Sandbox / preview (RED until DS)."""

import pytest
from fastapi.testclient import TestClient

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "org_admin",
}


@pytest.mark.atdd
@pytest.mark.epic5_atdd
def test_story_52_sandbox_run_endpoint(client: TestClient):
    """5.2: run flow in sandbox; no production send."""
    r = client.post(
        "/v1/me/flows/atdd-flow/sandbox-run",
        headers=_HDR,
        json={"fixture_message": {"type": "text", "body": "hi"}},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data.get("environment") == "sandbox"
    assert "persisted" in data
    assert "fixture_fingerprint" in data
    trace = data.get("trace") or []
    joined = "\n".join(trace)
    assert "sandbox:" in joined
    assert "production WhatsApp" in joined or "Meta send" in joined

"""ATDD Story 5.3 - Publish com permissao e ambiente."""

import pytest
from fastapi.testclient import TestClient

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "org_admin",
}


@pytest.mark.atdd
@pytest.mark.epic5_atdd
def test_story_53_publish_flow_endpoint(client: TestClient):
    """5.3: publish flow to target environment with audit."""
    r = client.post(
        "/v1/me/flows/atdd-flow/publish",
        headers=_HDR,
        json={"environment": "staging"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data.get("environment") == "staging"
    assert isinstance(data.get("idempotent_repeat"), bool)
    assert "activation_id" in data


@pytest.mark.atdd
@pytest.mark.epic5_atdd
def test_story_53_publish_idempotent_repeat(client: TestClient):
    r = client.post(
        "/v1/me/flows/atdd-flow/publish",
        headers=_HDR,
        json={"environment": "development"},
    )
    assert r.status_code == 200, r.text
    r2 = client.post(
        "/v1/me/flows/atdd-flow/publish",
        headers=_HDR,
        json={"environment": "development"},
    )
    assert r2.status_code == 200, r2.text
    assert r2.json().get("idempotent_repeat") is True

"""ATDD Story 5.3 - Publish com permissao e ambiente (RED until DS)."""

import pytest
from fastapi.testclient import TestClient

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "org_admin",
}


@pytest.mark.atdd
def test_story_53_publish_flow_endpoint(client: TestClient):
    """5.3: publish flow to target environment with audit."""
    r = client.post(
        "/v1/me/flows/atdd-flow/publish",
        headers=_HDR,
        json={"environment": "staging"},
    )
    assert r.status_code in (200, 201), r.text

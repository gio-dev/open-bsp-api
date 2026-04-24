"""ATDD Story 9.5 - Registo consentimento (RED until DS)."""

import pytest
from fastapi.testclient import TestClient

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "org_admin",
}


@pytest.mark.atdd
def test_story_95_consent_log(client: TestClient):
    """9.5: consent log query (links DSAR)."""
    r = client.get("/v1/me/governance/consents", headers=_HDR)
    assert r.status_code == 200, r.text

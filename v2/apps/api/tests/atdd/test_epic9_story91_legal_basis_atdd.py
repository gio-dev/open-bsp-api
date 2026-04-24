"""ATDD Story 9.1 - Finalidades e bases legais (RED until DS)."""

import pytest
from fastapi.testclient import TestClient

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "org_admin",
}


@pytest.mark.atdd
def test_story_91_legal_basis_records(client: TestClient):
    """9.1: legal basis / purposes per flow."""
    r = client.get("/v1/me/governance/legal-basis", headers=_HDR)
    assert r.status_code == 200, r.text

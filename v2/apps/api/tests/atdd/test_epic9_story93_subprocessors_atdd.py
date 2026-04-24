"""ATDD Story 9.3 - Lista subprocessadores (RED until DS)."""

import pytest
from fastapi.testclient import TestClient

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "org_admin",
}


@pytest.mark.atdd
def test_story_93_subprocessors_list(client: TestClient):
    """9.3: subprocessor list with version/date."""
    r = client.get("/v1/me/governance/subprocessors", headers=_HDR)
    assert r.status_code == 200, r.text

"""ATDD Story 9.2 - DSAR pedidos e ACK (RED until DS)."""

import pytest
from fastapi.testclient import TestClient

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "org_admin",
}


@pytest.mark.atdd
def test_story_92_dsar_request_create(client: TestClient):
    """9.2: create DSAR request (MVP hybrid)."""
    r = client.post(
        "/v1/me/dsar/requests",
        headers=_HDR,
        json={"type": "access", "subject_ref": "atdd-subject-1"},
    )
    assert r.status_code in (200, 201), r.text

"""ATDD Story 6.3 - Disclosure e opt-in granular (RED until DS)."""

import pytest
from fastapi.testclient import TestClient

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "org_admin",
}


@pytest.mark.atdd
def test_story_63_contact_preferences_endpoint(client: TestClient):
    """6.3: LGPD preferences per contact (read path)."""
    r = client.get(
        "/v1/me/contacts/atdd-contact/preferences",
        headers=_HDR,
    )
    assert r.status_code == 200, r.text

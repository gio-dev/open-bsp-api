"""ATDD Story 6.3 - Disclosure e opt-in granular (RED until DS)."""

import pytest
from app.atdd_fixture_ids import ATDD_CONTACT_PREFERENCES_ID
from fastapi.testclient import TestClient

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "org_admin",
}

pytestmark = [pytest.mark.atdd, pytest.mark.epic6_atdd]


def test_story_63_contact_preferences_endpoint(client: TestClient) -> None:
    """6.3: LGPD preferences per contact (read path)."""
    r = client.get(
        f"/v1/me/contacts/{ATDD_CONTACT_PREFERENCES_ID}/preferences",
        headers=_HDR,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["contact_id"] == ATDD_CONTACT_PREFERENCES_ID
    assert data["marketing_opt_in"] is False
    assert data["transactional_allowed"] is True
    assert data["disclosure_copy_slug"] == "baseline-v1"
    assert isinstance(data["updated_at"], str) and data["updated_at"]
    assert data.get("marketing_consent_recorded_at") is None

"""ATDD Story 6.4 - Acessibilidade do embed (RED until DS)."""

import pytest
from fastapi.testclient import TestClient

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "org_admin",
}

pytestmark = [pytest.mark.atdd, pytest.mark.epic6_atdd]


@pytest.mark.atdd
def test_story_64_embed_a11y_status_endpoint(client: TestClient):
    """6.4: metadados a11y embed para CI (200 + corpo)."""
    r = client.get("/v1/me/embed/a11y-status", headers=_HDR)
    assert r.status_code == 200, r.text
    body = r.json()
    for key in ("wcag_target", "spa_embed_route", "audited_journeys", "tooling_note"):
        assert key in body, body

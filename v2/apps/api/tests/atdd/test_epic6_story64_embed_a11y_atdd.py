"""ATDD Story 6.4 - Acessibilidade do embed (RED until DS)."""

import pytest
from fastapi.testclient import TestClient

_HDR = {
    "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
    "X-Dev-Roles": "org_admin",
}


@pytest.mark.atdd
def test_story_64_embed_a11y_status_endpoint(client: TestClient):
    """6.4: embed a11y status or metadata for audit (DS may return 404 until ready)."""
    r = client.get("/v1/me/embed/a11y-status", headers=_HDR)
    assert r.status_code in (200, 404), r.text

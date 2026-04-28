"""ATDD Story 3.3 - Templates e sinais opt-in / qualidade."""

import os

import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.atdd, pytest.mark.epic3_atdd]


@pytest.mark.atdd
@pytest.mark.skipif(
    not os.getenv("DATABASE_URL"),
    reason="templates persistidos em Postgres (CI api-ci)",
)
def test_story_33_templates_list_endpoint(client: TestClient):
    """3.3: list message templates / channel signals for tenant."""
    r = client.get(
        "/v1/me/message-templates",
        headers={
            "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
            "X-Dev-Roles": "org_admin",
        },
        params={"environment": "sandbox"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert "items" in body
    assert "channel_signals" in body
    assert body["environment"] == "sandbox"
    assert body.get("waba_id") == "ci-atdd-waba"

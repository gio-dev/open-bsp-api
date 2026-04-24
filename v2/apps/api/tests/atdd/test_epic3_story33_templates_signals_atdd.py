"""ATDD Story 3.3 - Templates e sinais opt-in / qualidade (RED until DS)."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.atdd
def test_story_33_templates_list_endpoint(client: TestClient):
    """3.3: list message templates / channel signals for tenant."""
    r = client.get(
        "/v1/me/message-templates",
        headers={
            "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
            "X-Dev-Roles": "org_admin",
        },
    )
    assert r.status_code == 200, r.text

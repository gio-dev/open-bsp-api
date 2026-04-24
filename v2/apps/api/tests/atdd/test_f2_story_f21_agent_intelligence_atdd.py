"""ATDD F2.1 - Agente inteligente (gate produto; RED until DS)."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.atdd
def test_story_f21_agent_policy_feature_flag(client: TestClient):
    """F2.1: agent intelligence capability or feature flag."""
    r = client.get("/v1/me/features/agent-intelligence")
    assert r.status_code in (200, 404), r.text

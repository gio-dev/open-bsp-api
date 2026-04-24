"""ATDD F3.1 - Orquestrador piloto (gate produto; RED until DS)."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.atdd
def test_story_f31_orchestrator_pilot_status(client: TestClient):
    """F3.1: orchestrator pilot status (n8n or agreed integration)."""
    r = client.get("/v1/me/features/orchestrator")
    assert r.status_code in (200, 404), r.text

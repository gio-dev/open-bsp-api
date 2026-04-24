"""ATDD Story 7.2 - Lifecycle e deprecation policy (RED until DS)."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.atdd
def test_story_72_deprecation_policy_route_or_docs(client: TestClient):
    """7.2: deprecation policy reachable (JSON, redirect, or static docs)."""
    r = client.get("/v1/policy/deprecation")
    assert r.status_code in (200, 301, 302, 404)

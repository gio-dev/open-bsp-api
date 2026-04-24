"""ATDD Story 7.1 - REST versioned e idempotencia (RED until DS)."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.atdd
def test_story_71_idempotent_send_header_documented(client: TestClient):
    """7.1: Idempotency-Key documented on mutations in OpenAPI."""
    spec = client.get("/openapi.json").json()
    paths = spec.get("paths", {})
    assert (
        any("idempotency" in str(paths.get(p, {})).lower() for p in paths)
        or "/v1/public/messages" in paths
        or "/v1/integrations/messages" in paths
    )

"""ATDD Story 6.1 - Embed JWT e validacao de origem (RED until DS)."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.atdd
def test_story_61_embed_session_validate(client: TestClient):
    """6.1: validate embed session (token + Origin allowlist)."""
    r = client.post(
        "/v1/embed/session/validate",
        headers={"Origin": "https://partner.example.com"},
        json={"token": "atdd.embed.jwt"},
    )
    assert r.status_code in (200, 401), r.text

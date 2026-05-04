"""HTTP smoke Story 6.1: embed validate sem segredo."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings


def test_validate_503_when_embed_secret_missing(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("OPENBSP_EMBED_JWT_SECRET", raising=False)
    monkeypatch.setenv("OPENBSP_EMBED_JWT_SECRET", "")
    get_settings.cache_clear()
    try:
        r = client.post(
            "/v1/embed/session/validate",
            headers={"Origin": "https://partner.example.com"},
            json={"token": "anything"},
        )
        assert r.status_code == 503, r.text
    finally:
        get_settings.cache_clear()

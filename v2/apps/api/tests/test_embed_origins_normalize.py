"""Unit: normalizacao de Origin para embed (Story 6.1)."""

from __future__ import annotations

import pytest
from app.embed.origins import normalize_browser_origin


def test_normalize_https_no_port() -> None:
    assert normalize_browser_origin("  HTTPS://Example.COM  ") == "https://example.com"


def test_normalize_with_port() -> None:
    assert normalize_browser_origin("http://localhost:5173") == "http://localhost:5173"


def test_normalize_rejects_path() -> None:
    with pytest.raises(ValueError, match="path, query or fragment"):
        normalize_browser_origin("https://a.com/foo")


def test_normalize_rejects_query() -> None:
    with pytest.raises(ValueError, match="path, query or fragment"):
        normalize_browser_origin("https://a.com?x=1")


def test_normalize_rejects_bad_scheme() -> None:
    with pytest.raises(ValueError, match="scheme"):
        normalize_browser_origin("ftp://a.com")


def test_normalize_rejects_missing_host() -> None:
    with pytest.raises(ValueError, match="netloc"):
        normalize_browser_origin("https://")

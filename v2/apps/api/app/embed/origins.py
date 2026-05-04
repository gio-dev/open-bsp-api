"""Normalizacao de cabecalho Origin (lista branca iframe)."""

from __future__ import annotations

from urllib.parse import urlparse


def normalize_browser_origin(raw: str) -> str:
    """Valor canonico tipo `https://host` ou `https://host:port` (minusculas)."""
    t = raw.strip()
    pr = urlparse(t)
    scheme = pr.scheme.lower()
    if scheme not in ("http", "https"):
        raise ValueError("origin scheme must be http or https")
    netloc = (pr.netloc or "").strip()
    if not netloc:
        raise ValueError("origin netloc missing")
    if pr.path not in ("", "/") or pr.query or pr.fragment:
        raise ValueError("origin must not include path, query or fragment")
    return f"{scheme}://{netloc.lower()}"

"""Versao semantica publicada (CHANGELOG / OpenAPI info.version)."""

from __future__ import annotations


def api_semantic_version() -> str:
    """Valor do pacote instalado (equivalente ao `pyproject.toml` / release)."""
    try:
        from importlib.metadata import PackageNotFoundError, version

        return version("openbsp-api")
    except (PackageNotFoundError, ValueError, OSError):
        return "0.1.0"

"""Unit: hashing de API keys (Story 2.3)."""

from app.core.api_key_crypto import (
    generate_api_key_material,
    hash_api_secret,
    verify_api_secret,
)


def test_hash_roundtrip() -> None:
    _, full = generate_api_key_material()
    stored = hash_api_secret(full)
    assert verify_api_secret(full, stored)
    assert not verify_api_secret(full + "x", stored)
    assert not verify_api_secret("wrong", stored)


def test_prefix_and_secret_shape() -> None:
    prefix, full = generate_api_key_material()
    assert full.startswith(prefix + ".")

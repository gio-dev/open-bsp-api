"""Hashing segredo de API key (PBKDF2; sem dependencias extra). Story 2.3."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets

_ITERATIONS = 600_000
_DKLEN = 32


def generate_api_key_material() -> tuple[str, str]:
    """Devolve (key_prefix, full_secret). O segredo completo mostrado uma vez no 201."""
    prefix = "obsp_" + secrets.token_urlsafe(8)[:12].rstrip("=")
    suffix = secrets.token_urlsafe(36)
    full = f"{prefix}.{suffix}"
    return prefix, full


def hash_api_secret(plaintext: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        plaintext.encode("utf-8"),
        salt,
        _ITERATIONS,
        dklen=_DKLEN,
    )
    blob = base64.urlsafe_b64encode(salt + _ITERATIONS.to_bytes(4, "big") + dk).decode(
        "ascii"
    )
    return f"v2${blob}"


def verify_api_secret(plaintext: str, stored: str) -> bool:
    if not stored.startswith("v2$"):
        return False
    try:
        raw = base64.urlsafe_b64decode(stored[3:].encode("ascii"))
    except (ValueError, OSError):
        return False
    if len(raw) < 16 + 4 + _DKLEN:
        return False
    salt, it_bytes, dk = raw[:16], raw[16:20], raw[20:]
    iterations = int.from_bytes(it_bytes, "big")
    cand = hashlib.pbkdf2_hmac(
        "sha256",
        plaintext.encode("utf-8"),
        salt,
        iterations,
        dklen=_DKLEN,
    )
    return hmac.compare_digest(cand, dk)

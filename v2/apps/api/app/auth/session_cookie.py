"""Cookie assinado (HMAC-SHA256) para sessao da consola."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any


def encode_payload(payload: dict[str, Any], secret: str) -> str:
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    b64 = base64.urlsafe_b64encode(body).decode().rstrip("=")
    sig = hmac.new(secret.encode(), b64.encode(), hashlib.sha256).hexdigest()
    return f"{b64}.{sig}"


def decode_payload(token: str, secret: str) -> dict[str, Any]:
    try:
        b64, sig = token.rsplit(".", 1)
    except ValueError as e:
        raise ValueError("invalid token") from e
    expected = hmac.new(secret.encode(), b64.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        raise ValueError("bad signature")
    pad = "=" * (-len(b64) % 4)
    data = base64.urlsafe_b64decode(b64 + pad)
    d = json.loads(data.decode())
    raw_exp = d.get("exp")
    if raw_exp is None:
        raise ValueError("missing exp")
    try:
        exp = int(raw_exp)
    except (TypeError, ValueError) as e:
        raise ValueError("invalid exp") from e
    if exp <= 0:
        raise ValueError("invalid exp")
    if time.time() > exp:
        raise ValueError("expired")
    return d

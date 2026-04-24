"""Unit tests: cookie assinado da sessao (Story 2.1)."""

import time

import pytest
from app.auth.session_cookie import decode_payload, encode_payload


def test_session_cookie_roundtrip() -> None:
    secret = "unit-secret"
    now = int(time.time())
    data = {"v": 1, "uid": "u1", "tid": "t1", "roles": ["org_admin"], "exp": now + 60}
    tok = encode_payload(data, secret)
    out = decode_payload(tok, secret)
    assert out["uid"] == "u1"
    assert out["roles"] == ["org_admin"]


def test_session_cookie_rejects_bad_sig() -> None:
    tok = encode_payload({"exp": int(time.time()) + 60}, "a")
    with pytest.raises(ValueError, match="bad signature"):
        decode_payload(tok, "other-secret")


def test_session_cookie_expired() -> None:
    tok = encode_payload({"exp": int(time.time()) - 10}, "sec")
    with pytest.raises(ValueError, match="expired"):
        decode_payload(tok, "sec")


def test_session_cookie_rejects_zero_exp() -> None:
    tok = encode_payload({"exp": 0, "k": 1}, "sec")
    with pytest.raises(ValueError, match="invalid exp"):
        decode_payload(tok, "sec")


def test_session_cookie_rejects_missing_exp() -> None:
    tok = encode_payload({"k": 1, "x": 2}, "sec")
    with pytest.raises(ValueError, match="missing exp"):
        decode_payload(tok, "sec")

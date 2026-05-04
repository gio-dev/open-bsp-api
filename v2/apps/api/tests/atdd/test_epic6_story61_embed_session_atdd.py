"""ATDD Story 6.1 - Embed JWT e validacao de origem."""

import os
import time

import pytest
from fastapi.testclient import TestClient

from app.auth.session_cookie import encode_payload

TENANT_ATDD = "11111111-1111-4111-8111-111111111111"
USER_ATDD = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"


@pytest.mark.atdd
@pytest.mark.epic6_atdd
def test_story_61_embed_session_validate(client: TestClient) -> None:
    """6.1: validate embed session (token + Origin allowlist + ci_seed)."""
    secret = os.environ["OPENBSP_EMBED_JWT_SECRET"]
    tok = encode_payload(
        {
            "v": 1,
            "tid": TENANT_ATDD,
            "uid": USER_ATDD,
            "exp": int(time.time()) + 3600,
        },
        secret,
    )
    r = client.post(
        "/v1/embed/session/validate",
        headers={"Origin": "https://partner.example.com"},
        json={"token": tok},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["valid"] is True
    assert body["tenant_id"] == TENANT_ATDD
    assert body["actor_user_id"] == USER_ATDD

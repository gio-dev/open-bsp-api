"""ATDD Story 7.1: REST /v1, OpenAPI idempotency contract, smoke de duplicado."""

from __future__ import annotations

import os
import time

import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.atdd, pytest.mark.epic7_atdd]

TENANT = "11111111-1111-4111-8111-111111111111"


@pytest.mark.atdd
def test_story_71_openapi_v1_contract_and_messages_send_headers(
    client: TestClient,
) -> None:
    """7.1: OpenAPI `/v1`, messages/send, Idempotency-Key, 401/429/503 + Retry-After."""
    spec = client.get("/openapi.json").json()
    info_desc = (spec.get("info") or {}).get("description") or ""
    assert "/v1" in info_desc

    op = spec.get("paths", {}).get("/v1/me/messages/send", {}).get("post") or {}
    assert op, "/v1/me/messages/send POST must exist in OpenAPI"
    params = op.get("parameters") or []
    names = [p.get("name") for p in params]
    assert "Idempotency-Key" in names

    responses = op.get("responses") or {}
    assert "401" in responses
    assert "429" in responses
    hdr429 = (responses["429"].get("headers") or {}).get("Retry-After")
    assert hdr429 is not None, "429 must document Retry-After"

    assert "503" in responses
    hdr503 = (responses["503"].get("headers") or {}).get("Retry-After")
    assert hdr503 is not None, "503 must document Retry-After"


@pytest.mark.atdd
@pytest.mark.skipif(
    not os.getenv("DATABASE_URL") or not os.getenv("ALEMBIC_SYNC_URL"),
    reason="needs DATABASE_URL and ALEMBIC_SYNC_URL (api-ci postgres)",
)
def test_story_71_idempotency_key_duplicate_post_returns_same_ack(
    client: TestClient,
) -> None:
    """7.1: dois POST com o mesmo Idempotency-Key -> mesmo id (202)."""
    key = f"idem-atdd71-{time.time_ns()}"
    headers = {
        "X-Dev-Tenant-Id": TENANT,
        "X-Dev-Roles": "operator",
        "Idempotency-Key": key,
    }
    body = {
        "to": "+351920000071",
        "type": "text",
        "text": {"body": "atdd-71-idempotency"},
        "environment": "sandbox",
    }
    r1 = client.post("/v1/me/messages/send", headers=headers, json=body)
    r2 = client.post("/v1/me/messages/send", headers=headers, json=body)
    assert r1.status_code == 202, r1.text
    assert r2.status_code == 202, r2.text
    assert r1.json()["id"] == r2.json()["id"]

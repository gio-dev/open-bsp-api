"""Story 6.1: validate embed session com allowlist + binding eor."""

from __future__ import annotations

import os
import time
import uuid

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.auth.session_cookie import encode_payload

HDR = {
    "X-Dev-Tenant-Id": "",
    "X-Dev-User-Id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
    "X-Dev-Roles": "org_admin",
}

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL") or not os.getenv("ALEMBIC_SYNC_URL"),
    reason="needs DATABASE_URL and ALEMBIC_SYNC_URL (CI postgres)",
)


@pytest.fixture
def embed_ctx() -> dict[str, str]:
    tid = uuid.uuid4()
    admin_url = os.environ["ALEMBIC_SYNC_URL"]
    secret = os.environ.get(
        "OPENBSP_EMBED_JWT_SECRET",
        "test-openbsp-embed-jwt-secret-atdd-32chars",
    )
    with psycopg.connect(admin_url, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO tenants (id) VALUES (%s)", (str(tid),))
            cur.execute(
                """
                INSERT INTO tenant_embed_origins (id, tenant_id, origin)
                VALUES (%s::uuid, %s::uuid, %s)
                """,
                (str(uuid.uuid4()), str(tid), "https://partner.example.test"),
            )
    hdr = {**HDR, "X-Dev-Tenant-Id": str(tid)}
    yield {"tid": str(tid), "hdr": hdr, "secret": secret}
    with psycopg.connect(admin_url, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tenants WHERE id = %s::uuid", (str(tid),))


@pytest.mark.integration
def test_validate_happy_path(client: TestClient, embed_ctx: dict[str, str]) -> None:
    tid = embed_ctx["tid"]
    secret = embed_ctx["secret"]
    now = int(time.time())
    tok = encode_payload(
        {"v": 1, "tid": tid, "exp": now + 7200},
        secret,
    )
    r = client.post(
        "/v1/embed/session/validate",
        headers={"Origin": "https://partner.example.test"},
        json={"token": tok},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["tenant_id"] == tid


@pytest.mark.integration
def test_validate_rejects_wrong_origin(
    client: TestClient, embed_ctx: dict[str, str]
) -> None:
    tid = embed_ctx["tid"]
    secret = embed_ctx["secret"]
    now = int(time.time())
    tok = encode_payload({"v": 1, "tid": tid, "exp": now + 7200}, secret)
    r = client.post(
        "/v1/embed/session/validate",
        headers={"Origin": "https://evil.example.test"},
        json={"token": tok},
    )
    assert r.status_code == 401, r.text


@pytest.mark.integration
def test_validate_eor_binding_mismatch(
    client: TestClient, embed_ctx: dict[str, str]
) -> None:
    tid = embed_ctx["tid"]
    secret = embed_ctx["secret"]
    now = int(time.time())
    tok = encode_payload(
        {
            "v": 1,
            "tid": tid,
            "exp": now + 7200,
            "eor": "https://partner.example.test",
        },
        secret,
    )
    r = client.post(
        "/v1/embed/session/validate",
        headers={"Origin": "https://other.example.test"},
        json={"token": tok},
    )
    assert r.status_code == 401, r.text


@pytest.mark.integration
def test_validate_expired_token(client: TestClient, embed_ctx: dict[str, str]) -> None:
    tid = embed_ctx["tid"]
    secret = embed_ctx["secret"]
    now = int(time.time())
    tok = encode_payload(
        {"v": 1, "tid": tid, "exp": now - 60},
        secret,
    )
    r = client.post(
        "/v1/embed/session/validate",
        headers={"Origin": "https://partner.example.test"},
        json={"token": tok},
    )
    assert r.status_code == 401, r.text


@pytest.mark.integration
def test_mint_rejects_embed_origin_not_allowlisted(
    client: TestClient, embed_ctx: dict[str, str]
) -> None:
    hdr = embed_ctx["hdr"]
    r = client.post(
        "/v1/me/embed/token",
        headers=hdr,
        json={
            "ttl_seconds": 120,
            "embed_origin": "https://not-in-allowlist.example.test",
        },
    )
    assert r.status_code == 400, r.text
    assert "allowlist" in r.json().get("message", "").lower()


@pytest.mark.integration
def test_mint_via_me_route(client: TestClient, embed_ctx: dict[str, str]) -> None:
    tid = embed_ctx["tid"]
    hdr = embed_ctx["hdr"]
    r = client.post(
        "/v1/me/embed/token",
        headers=hdr,
        json={"ttl_seconds": 120, "embed_origin": "https://partner.example.test"},
    )
    assert r.status_code == 201, r.text
    tok = r.json()["token"]

    r2 = client.post(
        "/v1/embed/session/validate",
        headers={"Origin": "https://partner.example.test"},
        json={"token": tok},
    )
    assert r2.status_code == 200, r2.text
    assert r2.json()["tenant_id"] == tid

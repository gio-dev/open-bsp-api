"""Story 4.1: inbox lista + thread."""

from __future__ import annotations

import os

import psycopg
import pytest
from fastapi.testclient import TestClient

TENANT = "11111111-1111-4111-8111-111111111111"

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL") or not os.getenv("ALEMBIC_SYNC_URL"),
    reason="needs DATABASE_URL and ALEMBIC_SYNC_URL (CI postgres)",
)


@pytest.mark.integration
def test_inbox_list_sandbox_includes_atdd_conv(client: TestClient) -> None:
    r = client.get(
        "/v1/me/conversations",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "operator",
        },
        params={"environment": "sandbox"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert "header" in data and "items" in data
    assert isinstance(data["header"]["tenant_display_name"], str)
    assert data["header"]["environment"] == "sandbox"
    assert data["header"]["waba"] is not None
    assert data["header"]["waba"]["waba_id"] == "ci-atdd-waba"
    ids = {x["id"] for x in data["items"]}
    assert "atdd-conv-1" in ids


@pytest.mark.integration
def test_inbox_thread_empty_ok(client: TestClient) -> None:
    r = client.get(
        "/v1/me/conversations/atdd-conv-1/messages",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "agent",
        },
        params={"environment": "sandbox"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["conversation_id"] == "atdd-conv-1"
    assert isinstance(body["items"], list)


@pytest.mark.integration
def test_inbox_thread_unknown_404(client: TestClient) -> None:
    r = client.get(
        "/v1/me/conversations/no-such-conv/messages",
        headers={
            "X-Dev-Tenant-Id": TENANT,
            "X-Dev-Roles": "viewer",
        },
        params={"environment": "sandbox"},
    )
    assert r.status_code == 404, r.text


@pytest.mark.integration
def test_inbox_multiple_lines_require_phone_number_id(
    client: TestClient,
) -> None:
    extra_row = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa04"
    admin = os.environ["ALEMBIC_SYNC_URL"]
    try:
        with psycopg.connect(admin) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO waba_phone_numbers
                      (id, tenant_id, waba_id, phone_number_id, display_phone_number,
                       environment, status)
                    VALUES (%s::uuid, %s::uuid, %s, %s, %s, %s, 'active')
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        extra_row,
                        TENANT,
                        "ci-atdd-waba",
                        "ci-atdd-phone-2",
                        "+15550004444",
                        "sandbox",
                    ),
                )
            conn.commit()

        r = client.get(
            "/v1/me/conversations",
            headers={
                "X-Dev-Tenant-Id": TENANT,
                "X-Dev-Roles": "operator",
            },
            params={"environment": "sandbox"},
        )
        assert r.status_code == 409, r.text
        assert "phone_number_id" in r.json().get("message", "").lower()

        r2 = client.get(
            "/v1/me/conversations",
            headers={
                "X-Dev-Tenant-Id": TENANT,
                "X-Dev-Roles": "operator",
            },
            params={"environment": "sandbox", "phone_number_id": "ci-atdd-phone-1"},
        )
        assert r2.status_code == 200, r2.text
        assert r2.json()["header"]["waba"]["phone_number_id"] == "ci-atdd-phone-1"

        r3 = client.get(
            "/v1/me/conversations/atdd-conv-1/messages",
            headers={
                "X-Dev-Tenant-Id": TENANT,
                "X-Dev-Roles": "operator",
            },
            params={"environment": "sandbox", "phone_number_id": "ci-atdd-phone-1"},
        )
        assert r3.status_code == 200, r3.text
    finally:
        with psycopg.connect(admin) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM waba_phone_numbers WHERE id = %s::uuid",
                    (extra_row,),
                )
            conn.commit()

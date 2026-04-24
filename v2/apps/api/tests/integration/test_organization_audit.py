"""Story 1.3: audit_events append-only on organization PATCH."""

from __future__ import annotations

import os
import uuid

import psycopg
import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL") or not os.getenv("ALEMBIC_SYNC_URL"),
    reason="needs DATABASE_URL and ALEMBIC_SYNC_URL (CI postgres)",
)


@pytest.mark.integration
def test_patch_organization_appends_audit_event(
    client: TestClient,
) -> None:
    admin_url = os.environ["ALEMBIC_SYNC_URL"]
    headers = {
        "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
        "X-Dev-Roles": "org_admin",
        "X-Dev-User-Id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
    }
    with psycopg.connect(admin_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM audit_events WHERE tenant_id = %s::uuid",
                ("11111111-1111-4111-8111-111111111111",),
            )
        conn.commit()

    probe = f"Audit probe {uuid.uuid4().hex[:8]}"
    r = client.patch(
        "/v1/me/organization",
        headers=headers,
        json={"display_name": probe},
    )
    assert r.status_code == 200, r.text

    with psycopg.connect(admin_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT count(*), max(summary) FROM audit_events "
                "WHERE tenant_id = %s::uuid AND resource_type = %s",
                ("11111111-1111-4111-8111-111111111111", "organization_profile"),
            )
            count, summary = cur.fetchone()
    assert count >= 1
    assert summary and "display_name" in summary

"""CI/dev seed data (RUN_CI_SEED=1). Uses superuser sync URL (ALEMBIC_SYNC_URL)."""

from __future__ import annotations

import os
import sys


def main() -> int:
    if os.environ.get("RUN_CI_SEED") != "1":
        return 0
    dsn = os.environ.get("ALEMBIC_SYNC_URL")
    if not dsn:
        print("RUN_CI_SEED=1 requires ALEMBIC_SYNC_URL", file=sys.stderr)
        return 1

    import psycopg

    tenant_id = "11111111-1111-4111-8111-111111111111"
    row_id = "22222222-2222-4222-8222-222222222222"
    console_user_id = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
    membership_id = "cccccccc-cccc-4ccc-8ccc-cccccccccccc"

    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tenants (id) VALUES (%s::uuid) ON CONFLICT DO NOTHING",
                (tenant_id,),
            )
            cur.execute(
                """
                INSERT INTO tenant_settings_stub
                  (id, tenant_id, display_name, timezone, operational_email)
                VALUES (%s::uuid, %s::uuid, %s, %s, %s)
                ON CONFLICT (tenant_id) DO UPDATE SET
                  display_name = EXCLUDED.display_name,
                  timezone = EXCLUDED.timezone,
                  operational_email = EXCLUDED.operational_email
                """,
                (row_id, tenant_id, "ATDD Default", "Europe/Lisbon", ""),
            )
            cur.execute(
                """
                INSERT INTO console_users (id, oidc_sub, email)
                VALUES (%s::uuid, %s, %s)
                ON CONFLICT (oidc_sub) DO UPDATE SET email = EXCLUDED.email
                """,
                (console_user_id, "ci-atdd-sub", "atdd@local"),
            )
            cur.execute(
                """
                INSERT INTO tenant_memberships (id, user_id, tenant_id, role)
                VALUES (%s::uuid, %s::uuid, %s::uuid, 'org_admin')
                ON CONFLICT (user_id, tenant_id) DO UPDATE SET role = EXCLUDED.role
                """,
                (membership_id, console_user_id, tenant_id),
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

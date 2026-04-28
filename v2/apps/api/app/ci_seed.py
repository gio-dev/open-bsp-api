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
    waba_row_id = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
    atdd_tag_id = "dddddddd-dddd-4ddd-8ddd-dddddddddddd"
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
            cur.execute(
                """
                INSERT INTO waba_phone_numbers
                  (id, tenant_id, waba_id, phone_number_id, display_phone_number,
                   environment, status)
                VALUES (%s::uuid, %s::uuid, %s, %s, %s, %s, 'active')
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    waba_row_id,
                    tenant_id,
                    "ci-atdd-waba",
                    "ci-atdd-phone-1",
                    "+15550001111",
                    "sandbox",
                ),
            )
            cur.execute(
                """
                INSERT INTO inbox_conversations
                  (id, tenant_id, waba_id, contact_wa_id, environment, title,
                   waba_phone_number_id, last_activity_at)
                VALUES (%s, %s::uuid, %s, %s, %s, %s, %s::uuid, now())
                ON CONFLICT ON CONSTRAINT uq_inbox_conv_tenant_waba_contact DO NOTHING
                """,
                (
                    "atdd-conv-1",
                    tenant_id,
                    "ci-atdd-waba",
                    "15550009999",
                    "sandbox",
                    "ATDD inbox",
                    waba_row_id,
                ),
            )
            cur.execute(
                """
                INSERT INTO inbox_tags (id, tenant_id, name)
                VALUES (%s::uuid, %s::uuid, %s)
                ON CONFLICT ON CONSTRAINT uq_inbox_tag_tenant_name DO NOTHING
                """,
                (atdd_tag_id, tenant_id, "atdd-label"),
            )
            cur.execute(
                """
                INSERT INTO inbox_conversation_tags
                  (conversation_id, tag_id, tenant_id)
                VALUES (%s, %s::uuid, %s::uuid)
                ON CONFLICT (conversation_id, tag_id) DO NOTHING
                """,
                ("atdd-conv-1", atdd_tag_id, tenant_id),
            )
            cur.execute(
                """
                INSERT INTO inbox_conversation_handoffs
                  (conversation_id, tenant_id, intent_summary, bot_last_output,
                   handoff_state, queue_id)
                VALUES (%s, %s::uuid, %s, %s, %s, %s)
                ON CONFLICT (conversation_id) DO UPDATE SET
                  intent_summary = EXCLUDED.intent_summary,
                  bot_last_output = EXCLUDED.bot_last_output,
                  handoff_state = EXCLUDED.handoff_state,
                  queue_id = EXCLUDED.queue_id,
                  updated_at = now()
                """,
                (
                    "atdd-conv-1",
                    tenant_id,
                    "Cliente pede atendimento humano (ATDD).",
                    "A transferir para um agente.",
                    "queued",
                    "atdd-queue-default",
                ),
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

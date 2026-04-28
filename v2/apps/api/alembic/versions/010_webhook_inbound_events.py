"""webhook_inbound_events (fila ingresso Meta) + resolve_waba_tenant. Story 3.1.

Revision ID: 010
Revises: 009
Create Date: 2026-04-28

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text("""
        CREATE OR REPLACE FUNCTION public.resolve_waba_tenant(
          p_waba_id text,
          p_phone_number_id text
        ) RETURNS uuid
        LANGUAGE sql
        STABLE
        SECURITY DEFINER
        SET search_path = public
        AS $fn$
          SELECT w.tenant_id
          FROM waba_phone_numbers w
          WHERE w.waba_id = p_waba_id
            AND (
              p_phone_number_id IS NULL
              OR length(trim(p_phone_number_id)) = 0
              OR w.phone_number_id = p_phone_number_id
            )
          ORDER BY
            CASE
              WHEN p_phone_number_id IS NOT NULL
                AND length(trim(p_phone_number_id)) > 0
                AND w.phone_number_id = p_phone_number_id
              THEN 0
              ELSE 1
            END,
            w.created_at ASC
          LIMIT 1;
        $fn$
        """)
    )
    op.execute(
        sa.text(
            "REVOKE ALL ON FUNCTION public.resolve_waba_tenant(text, text) FROM PUBLIC"
        )
    )
    op.execute(
        sa.text(
            "GRANT EXECUTE ON FUNCTION public.resolve_waba_tenant(text, text) "
            "TO app_runtime"
        )
    )

    op.create_table(
        "webhook_inbound_events",
        sa.Column(
            "id",
            sa.Uuid(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("waba_id", sa.String(128), nullable=False),
        sa.Column("source_id", sa.String(256), nullable=False),
        sa.Column("event_kind", sa.String(32), nullable=False),
        sa.Column("payload", JSONB(), nullable=False),
        sa.Column("message_ts", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
    )
    op.create_unique_constraint(
        "uq_webhook_inbound_waba_source",
        "webhook_inbound_events",
        ["waba_id", "source_id"],
    )
    op.create_index(
        "ix_webhook_inbound_events_tenant_created",
        "webhook_inbound_events",
        ["tenant_id", "created_at"],
        unique=False,
    )

    op.execute(sa.text("ALTER TABLE webhook_inbound_events ENABLE ROW LEVEL SECURITY"))
    op.execute(sa.text("ALTER TABLE webhook_inbound_events FORCE ROW LEVEL SECURITY"))
    op.execute(
        sa.text("""
        CREATE POLICY webhook_inbound_events_isolation ON webhook_inbound_events
        FOR ALL
        USING (tenant_id::text = current_setting('app.tenant_id', true))
        WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true))
        """)
    )
    op.execute(
        sa.text(
            "GRANT SELECT, INSERT, UPDATE, DELETE ON webhook_inbound_events "
            "TO app_runtime"
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DROP POLICY IF EXISTS webhook_inbound_events_isolation "
            "ON webhook_inbound_events"
        )
    )
    op.drop_index(
        "ix_webhook_inbound_events_tenant_created", table_name="webhook_inbound_events"
    )
    op.drop_constraint(
        "uq_webhook_inbound_waba_source", "webhook_inbound_events", type_="unique"
    )
    op.drop_table("webhook_inbound_events")
    op.execute(
        sa.text("DROP FUNCTION IF EXISTS public.resolve_waba_tenant(text, text)")
    )

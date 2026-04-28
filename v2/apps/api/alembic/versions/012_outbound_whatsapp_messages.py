"""outbound_whatsapp_messages (Story 3.2) fila envio + estado.

Revision ID: 012
Revises: 011
Create Date: 2026-04-28

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "012"
down_revision: Union[str, None] = "011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "outbound_whatsapp_messages",
        sa.Column(
            "id",
            sa.Uuid(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("waba_phone_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("to_recipient", sa.String(32), nullable=False),
        sa.Column("message_type", sa.String(32), nullable=False),
        sa.Column("payload", JSONB(), nullable=False),
        sa.Column(
            "status",
            sa.String(32),
            nullable=False,
            server_default=sa.text("'queued'"),
        ),
        sa.Column("idempotency_key", sa.String(128), nullable=True),
        sa.Column("meta_message_id", sa.String(256), nullable=True),
        sa.Column("upstream_fault", sa.String(16), nullable=True),
        sa.Column("error_code", sa.String(64), nullable=True),
        sa.Column("error_message", sa.String(1024), nullable=True),
        sa.Column(
            "attempt_count",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["waba_phone_id"],
            ["waba_phone_numbers.id"],
            ondelete="RESTRICT",
        ),
    )
    op.create_index(
        "ix_outbound_wa_msg_tenant_status",
        "outbound_whatsapp_messages",
        ["tenant_id", "status", "created_at"],
        unique=False,
    )
    op.execute(
        sa.text(
            """
            CREATE UNIQUE INDEX ix_outbound_wa_msg_tenant_idempotency
            ON outbound_whatsapp_messages (tenant_id, idempotency_key)
            WHERE (idempotency_key IS NOT NULL)
            """
        )
    )
    op.execute(
        sa.text("ALTER TABLE outbound_whatsapp_messages ENABLE ROW LEVEL SECURITY")
    )
    op.execute(
        sa.text("ALTER TABLE outbound_whatsapp_messages FORCE ROW LEVEL SECURITY")
    )
    op.execute(
        sa.text("""
        CREATE POLICY outbound_wa_msg_isolation ON outbound_whatsapp_messages
        FOR ALL
        USING (tenant_id::text = current_setting('app.tenant_id', true))
        WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true))
        """)
    )
    op.execute(
        sa.text(
            "GRANT SELECT, INSERT, UPDATE, DELETE ON outbound_whatsapp_messages "
            "TO app_runtime"
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DROP POLICY IF EXISTS outbound_wa_msg_isolation "
            "ON outbound_whatsapp_messages"
        )
    )
    op.drop_index(
        "ix_outbound_wa_msg_tenant_status", table_name="outbound_whatsapp_messages"
    )
    op.execute(sa.text("DROP INDEX IF EXISTS ix_outbound_wa_msg_tenant_idempotency"))
    op.drop_table("outbound_whatsapp_messages")

"""inbox_conversations (Story 4.1) lista + thread.

Revision ID: 015
Revises: 014
Create Date: 2026-04-28

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "015"
down_revision: Union[str, None] = "014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "inbox_conversations",
        sa.Column("id", sa.String(128), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("waba_id", sa.String(128), nullable=False),
        sa.Column("contact_wa_id", sa.String(32), nullable=False),
        sa.Column("environment", sa.String(32), nullable=False),
        sa.Column("title", sa.String(512), nullable=True),
        sa.Column("waba_phone_number_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=True),
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
            ["waba_phone_number_id"],
            ["waba_phone_numbers.id"],
            ondelete="SET NULL",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "waba_id",
            "contact_wa_id",
            name="uq_inbox_conv_tenant_waba_contact",
        ),
    )
    op.execute(
        sa.text(
            """
            CREATE INDEX ix_inbox_conv_tenant_env_activity
            ON inbox_conversations (
              tenant_id,
              environment,
              last_activity_at DESC NULLS LAST
            )
            """
        )
    )
    op.execute(sa.text("ALTER TABLE inbox_conversations ENABLE ROW LEVEL SECURITY"))
    op.execute(sa.text("ALTER TABLE inbox_conversations FORCE ROW LEVEL SECURITY"))
    op.execute(
        sa.text("""
        CREATE POLICY inbox_conversations_isolation ON inbox_conversations
        FOR ALL
        USING (tenant_id::text = current_setting('app.tenant_id', true))
        WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true))
        """)
    )
    op.execute(
        sa.text(
            "GRANT SELECT, INSERT, UPDATE, DELETE ON inbox_conversations TO app_runtime"
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DROP POLICY IF EXISTS inbox_conversations_isolation ON inbox_conversations"
        )
    )
    op.execute(sa.text("ALTER TABLE inbox_conversations NO FORCE ROW LEVEL SECURITY"))
    op.execute(sa.text("ALTER TABLE inbox_conversations DISABLE ROW LEVEL SECURITY"))
    op.drop_index("ix_inbox_conv_tenant_env_activity", table_name="inbox_conversations")
    op.drop_table("inbox_conversations")

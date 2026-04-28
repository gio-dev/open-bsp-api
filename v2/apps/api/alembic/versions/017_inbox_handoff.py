"""inbox_conversation_handoffs (Story 4.3) contexto handoff.

Revision ID: 017
Revises: 016
Create Date: 2026-04-28

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "017"
down_revision: Union[str, None] = "016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "inbox_conversation_handoffs",
        sa.Column("conversation_id", sa.String(128), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("intent_summary", sa.Text(), nullable=True),
        sa.Column("bot_last_output", sa.Text(), nullable=True),
        sa.Column(
            "handoff_state",
            sa.String(32),
            server_default=sa.text("'automated'"),
            nullable=False,
        ),
        sa.Column("queue_id", sa.String(128), nullable=True),
        sa.Column("claimed_by_user_id", sa.Uuid(as_uuid=True), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["inbox_conversations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["claimed_by_user_id"],
            ["console_users.id"],
            ondelete="SET NULL",
        ),
        sa.CheckConstraint(
            "handoff_state IN ("
            "'automated', 'pending_handoff', 'queued', 'accepted', 'failed'"
            ")",
            name="ck_inbox_handoff_state",
        ),
    )
    op.execute(
        sa.text("ALTER TABLE inbox_conversation_handoffs ENABLE ROW LEVEL SECURITY")
    )
    op.execute(
        sa.text("ALTER TABLE inbox_conversation_handoffs FORCE ROW LEVEL SECURITY")
    )
    op.execute(
        sa.text(
            """
            CREATE POLICY inbox_handoff_isolation ON inbox_conversation_handoffs
            FOR ALL
            USING (tenant_id::text = current_setting('app.tenant_id', true))
            WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true))
            """
        )
    )
    op.execute(
        sa.text(
            "GRANT SELECT, INSERT, UPDATE, DELETE ON inbox_conversation_handoffs "
            "TO app_runtime"
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DROP POLICY IF EXISTS inbox_handoff_isolation "
            "ON inbox_conversation_handoffs"
        )
    )
    op.execute(
        sa.text("ALTER TABLE inbox_conversation_handoffs NO FORCE ROW LEVEL SECURITY")
    )
    op.execute(
        sa.text("ALTER TABLE inbox_conversation_handoffs DISABLE ROW LEVEL SECURITY")
    )
    op.drop_table("inbox_conversation_handoffs")

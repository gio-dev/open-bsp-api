"""inbox tags + conversation_tags (Story 4.2).

Revision ID: 016
Revises: 015
Create Date: 2026-04-28

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "016"
down_revision: Union[str, None] = "015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "inbox_tags",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
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
        sa.UniqueConstraint("tenant_id", "name", name="uq_inbox_tag_tenant_name"),
    )
    op.create_index("ix_inbox_tags_tenant_id", "inbox_tags", ["tenant_id"])

    op.create_table(
        "inbox_conversation_tags",
        sa.Column("conversation_id", sa.String(128), nullable=False),
        sa.Column("tag_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["inbox_conversations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["inbox_tags.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("conversation_id", "tag_id"),
    )
    op.create_index(
        "ix_inbox_conv_tags_tenant_conv",
        "inbox_conversation_tags",
        ["tenant_id", "conversation_id"],
    )

    op.execute(sa.text("ALTER TABLE inbox_tags ENABLE ROW LEVEL SECURITY"))
    op.execute(sa.text("ALTER TABLE inbox_tags FORCE ROW LEVEL SECURITY"))
    op.execute(
        sa.text("""
        CREATE POLICY inbox_tags_isolation ON inbox_tags
        FOR ALL
        USING (tenant_id::text = current_setting('app.tenant_id', true))
        WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true))
        """)
    )
    op.execute(
        sa.text("GRANT SELECT, INSERT, UPDATE, DELETE ON inbox_tags TO app_runtime")
    )

    op.execute(sa.text("ALTER TABLE inbox_conversation_tags ENABLE ROW LEVEL SECURITY"))
    op.execute(sa.text("ALTER TABLE inbox_conversation_tags FORCE ROW LEVEL SECURITY"))
    op.execute(
        sa.text("""
        CREATE POLICY inbox_conversation_tags_isolation ON inbox_conversation_tags
        FOR ALL
        USING (tenant_id::text = current_setting('app.tenant_id', true))
        WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true))
        """)
    )
    op.execute(
        sa.text(
            "GRANT SELECT, INSERT, UPDATE, DELETE ON inbox_conversation_tags "
            "TO app_runtime"
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DROP POLICY IF EXISTS inbox_conversation_tags_isolation "
            "ON inbox_conversation_tags"
        )
    )
    op.execute(
        sa.text("ALTER TABLE inbox_conversation_tags NO FORCE ROW LEVEL SECURITY")
    )
    op.execute(
        sa.text("ALTER TABLE inbox_conversation_tags DISABLE ROW LEVEL SECURITY")
    )
    op.drop_index(
        "ix_inbox_conv_tags_tenant_conv",
        table_name="inbox_conversation_tags",
    )
    op.drop_table("inbox_conversation_tags")

    op.execute(sa.text("DROP POLICY IF EXISTS inbox_tags_isolation ON inbox_tags"))
    op.execute(sa.text("ALTER TABLE inbox_tags NO FORCE ROW LEVEL SECURITY"))
    op.execute(sa.text("ALTER TABLE inbox_tags DISABLE ROW LEVEL SECURITY"))
    op.drop_index("ix_inbox_tags_tenant_id", table_name="inbox_tags")
    op.drop_table("inbox_tags")

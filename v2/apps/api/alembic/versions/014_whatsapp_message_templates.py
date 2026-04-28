"""whatsapp_message_templates cache (Story 3.3) templates Meta + sinais.

Revision ID: 014
Revises: 013
Create Date: 2026-04-28

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "014"
down_revision: Union[str, None] = "013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "whatsapp_message_templates",
        sa.Column(
            "id",
            sa.Uuid(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("waba_id", sa.String(128), nullable=False),
        sa.Column("environment", sa.String(32), nullable=False),
        sa.Column("meta_template_id", sa.String(128), nullable=True),
        sa.Column("name", sa.String(512), nullable=False),
        sa.Column("language", sa.String(32), nullable=False),
        sa.Column("category", sa.String(64), nullable=True),
        sa.Column("display_status", sa.String(32), nullable=False),
        sa.Column("meta_status", sa.String(64), nullable=False),
        sa.Column("status_detail", sa.String(1024), nullable=True),
        sa.Column("quality_score", sa.String(32), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
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
    )
    op.create_index(
        "ix_wa_tpl_tenant_env_waba",
        "whatsapp_message_templates",
        ["tenant_id", "environment", "waba_id"],
        unique=False,
    )
    op.execute(
        sa.text(
            """
            CREATE UNIQUE INDEX ix_wa_tpl_tenant_waba_env_name_lang
            ON whatsapp_message_templates (
              tenant_id, waba_id, environment, name, language
            )
            """
        )
    )
    op.execute(
        sa.text("ALTER TABLE whatsapp_message_templates ENABLE ROW LEVEL SECURITY")
    )
    op.execute(
        sa.text("ALTER TABLE whatsapp_message_templates FORCE ROW LEVEL SECURITY")
    )
    op.execute(
        sa.text("""
        CREATE POLICY wa_msg_tpl_isolation ON whatsapp_message_templates
        FOR ALL
        USING (tenant_id::text = current_setting('app.tenant_id', true))
        WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true))
        """)
    )
    op.execute(
        sa.text(
            "GRANT SELECT, INSERT, UPDATE, DELETE ON whatsapp_message_templates "
            "TO app_runtime"
        )
    )
    op.create_table(
        "whatsapp_channel_snapshots",
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("waba_id", sa.String(128), nullable=False),
        sa.Column("environment", sa.String(32), nullable=False),
        sa.Column("quality_rating", sa.String(32), nullable=True),
        sa.Column("messaging_limit_tier", sa.String(64), nullable=True),
        sa.Column("signal_source", sa.String(32), nullable=False),
        sa.Column("notes", sa.String(512), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tenant_id", "waba_id", "environment"),
    )
    op.execute(
        sa.text("ALTER TABLE whatsapp_channel_snapshots ENABLE ROW LEVEL SECURITY")
    )
    op.execute(
        sa.text("ALTER TABLE whatsapp_channel_snapshots FORCE ROW LEVEL SECURITY")
    )
    op.execute(
        sa.text("""
        CREATE POLICY wa_ch_snap_isolation ON whatsapp_channel_snapshots
        FOR ALL
        USING (tenant_id::text = current_setting('app.tenant_id', true))
        WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true))
        """)
    )
    op.execute(
        sa.text(
            "GRANT SELECT, INSERT, UPDATE, DELETE ON whatsapp_channel_snapshots "
            "TO app_runtime"
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DROP POLICY IF EXISTS wa_ch_snap_isolation ON whatsapp_channel_snapshots"
        )
    )
    op.drop_table("whatsapp_channel_snapshots")
    op.execute(
        sa.text(
            "DROP POLICY IF EXISTS wa_msg_tpl_isolation ON whatsapp_message_templates"
        )
    )
    op.drop_index("ix_wa_tpl_tenant_env_waba", table_name="whatsapp_message_templates")
    op.execute(sa.text("DROP INDEX IF EXISTS ix_wa_tpl_tenant_waba_env_name_lang"))
    op.drop_table("whatsapp_message_templates")

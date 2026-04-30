"""tenant_flow_publish_activations: versao activa por ambiente (Story 5.3).

Revision ID: 020
Revises: 019
Create Date: 2026-04-30

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "020"
down_revision: Union[str, None] = "019"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenant_flow_publish_activations",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("flow_draft_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("flow_external_key", sa.String(128), nullable=True),
        sa.Column("environment", sa.String(32), nullable=False),
        sa.Column("definition_snapshot", JSONB(), nullable=False),
        sa.Column("definition_fingerprint", sa.String(64), nullable=False),
        sa.Column(
            "activated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("activated_by_user_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.CheckConstraint(
            "(flow_draft_id IS NOT NULL AND flow_external_key IS NULL) OR "
            "(flow_draft_id IS NULL AND flow_external_key IS NOT NULL)",
            name="ck_tenant_flow_publish_target_xor",
        ),
        sa.CheckConstraint(
            "environment IN ('development', 'staging', 'production')",
            name="ck_tenant_flow_publish_environment",
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["flow_draft_id"],
            ["tenant_flow_drafts.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "uq_tenant_flow_publish_draft_env",
        "tenant_flow_publish_activations",
        ["tenant_id", "flow_draft_id", "environment"],
        unique=True,
        postgresql_where=sa.text("flow_draft_id IS NOT NULL"),
    )
    op.create_index(
        "uq_tenant_flow_publish_extkey_env",
        "tenant_flow_publish_activations",
        ["tenant_id", "flow_external_key", "environment"],
        unique=True,
        postgresql_where=sa.text("flow_external_key IS NOT NULL"),
    )
    op.create_index(
        "ix_tenant_flow_publish_tenant_env",
        "tenant_flow_publish_activations",
        ["tenant_id", "environment"],
    )
    op.execute(
        sa.text("ALTER TABLE tenant_flow_publish_activations ENABLE ROW LEVEL SECURITY")
    )
    op.execute(
        sa.text("ALTER TABLE tenant_flow_publish_activations FORCE ROW LEVEL SECURITY")
    )
    op.execute(
        sa.text(
            """
            CREATE POLICY tenant_flow_publish_isolation
            ON tenant_flow_publish_activations
            FOR ALL
            USING (tenant_id::text = current_setting('app.tenant_id', true))
            WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true))
            """
        )
    )
    op.execute(
        sa.text(
            "GRANT SELECT, INSERT, UPDATE, DELETE ON tenant_flow_publish_activations "
            "TO app_runtime"
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DROP POLICY IF EXISTS tenant_flow_publish_isolation "
            "ON tenant_flow_publish_activations"
        )
    )
    op.execute(
        sa.text(
            "ALTER TABLE tenant_flow_publish_activations NO FORCE ROW LEVEL SECURITY"
        )
    )
    op.execute(
        sa.text(
            "ALTER TABLE tenant_flow_publish_activations DISABLE ROW LEVEL SECURITY"
        )
    )
    op.drop_index(
        "ix_tenant_flow_publish_tenant_env",
        table_name="tenant_flow_publish_activations",
    )
    op.drop_index(
        "uq_tenant_flow_publish_extkey_env",
        table_name="tenant_flow_publish_activations",
    )
    op.drop_index(
        "uq_tenant_flow_publish_draft_env",
        table_name="tenant_flow_publish_activations",
    )
    op.drop_table("tenant_flow_publish_activations")

"""tenant_flow_publish_versions: historico imutavel por publicacao material (Story 5.4).

Revision ID: 021
Revises: 020
Create Date: 2026-04-30

Append-only: app_runtime so SELECT, INSERT (sem UPDATE/DELETE).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "021"
down_revision: Union[str, None] = "020"
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenant_flow_publish_versions",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("flow_draft_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("flow_external_key", sa.String(128), nullable=True),
        sa.Column("environment", sa.String(32), nullable=False),
        sa.Column("definition_snapshot", JSONB(), nullable=False),
        sa.Column("definition_fingerprint", sa.String(64), nullable=False),
        sa.Column(
            "published_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("published_by_user_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("publish_activation_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.CheckConstraint(
            "(flow_draft_id IS NOT NULL AND flow_external_key IS NULL) OR "
            "(flow_draft_id IS NULL AND flow_external_key IS NOT NULL)",
            name="ck_tenant_flow_pv_target_xor",
        ),
        sa.CheckConstraint(
            "environment IN ('development', 'staging', 'production')",
            name="ck_tenant_flow_pv_environment",
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["flow_draft_id"],
            ["tenant_flow_drafts.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["publish_activation_id"],
            ["tenant_flow_publish_activations.id"],
            ondelete="SET NULL",
        ),
    )
    op.create_index(
        "ix_tfv_draft_hist",
        "tenant_flow_publish_versions",
        ["tenant_id", "flow_draft_id", "published_at"],
        postgresql_where=sa.text("flow_draft_id IS NOT NULL"),
    )
    op.create_index(
        "ix_tfv_extkey_hist",
        "tenant_flow_publish_versions",
        ["tenant_id", "flow_external_key", "published_at"],
        postgresql_where=sa.text("flow_external_key IS NOT NULL"),
    )
    op.execute(
        sa.text("ALTER TABLE tenant_flow_publish_versions ENABLE ROW LEVEL SECURITY")
    )
    op.execute(
        sa.text("ALTER TABLE tenant_flow_publish_versions FORCE ROW LEVEL SECURITY")
    )
    op.execute(
        sa.text(
            """
            CREATE POLICY tenant_flow_publish_versions_isolation
            ON tenant_flow_publish_versions
            FOR ALL
            USING (tenant_id::text = current_setting('app.tenant_id', true))
            WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true))
            """
        )
    )
    op.execute(
        sa.text("GRANT SELECT, INSERT ON tenant_flow_publish_versions TO app_runtime")
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DROP POLICY IF EXISTS tenant_flow_publish_versions_isolation "
            "ON tenant_flow_publish_versions"
        )
    )
    op.execute(
        sa.text("ALTER TABLE tenant_flow_publish_versions NO FORCE ROW LEVEL SECURITY")
    )
    op.execute(
        sa.text("ALTER TABLE tenant_flow_publish_versions DISABLE ROW LEVEL SECURITY")
    )
    op.drop_index("ix_tfv_extkey_hist", table_name="tenant_flow_publish_versions")
    op.drop_index("ix_tfv_draft_hist", table_name="tenant_flow_publish_versions")
    op.drop_table("tenant_flow_publish_versions")

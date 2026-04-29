"""tenant_flow_sandbox_runs (Story 5.2 preview / trace).

Revision ID: 019
Revises: 018
Create Date: 2026-04-29

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "019"
down_revision: Union[str, None] = "018"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenant_flow_sandbox_runs",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("flow_draft_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("flow_external_key", sa.String(128), nullable=True),
        sa.Column(
            "environment",
            sa.String(32),
            nullable=False,
            server_default="sandbox",
        ),
        sa.Column("fixture", JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("trace", JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("correlation_id", sa.String(128), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["flow_draft_id"],
            ["tenant_flow_drafts.id"],
            ondelete="SET NULL",
        ),
        sa.CheckConstraint(
            "environment IN ('sandbox')",
            name="ck_flow_sandbox_runs_environment",
        ),
    )
    op.create_index(
        "ix_tenant_flow_sandbox_runs_tenant_created",
        "tenant_flow_sandbox_runs",
        ["tenant_id", "created_at"],
    )
    op.execute(sa.text("ALTER TABLE tenant_flow_sandbox_runs ENABLE ROW LEVEL SECURITY"))
    op.execute(sa.text("ALTER TABLE tenant_flow_sandbox_runs FORCE ROW LEVEL SECURITY"))
    op.execute(
        sa.text(
            """
            CREATE POLICY tenant_flow_sandbox_runs_isolation ON tenant_flow_sandbox_runs
            FOR ALL
            USING (tenant_id::text = current_setting('app.tenant_id', true))
            WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true))
            """
        )
    )
    op.execute(
        sa.text(
            "GRANT SELECT, INSERT, UPDATE, DELETE ON tenant_flow_sandbox_runs "
            "TO app_runtime"
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DROP POLICY IF EXISTS tenant_flow_sandbox_runs_isolation "
            "ON tenant_flow_sandbox_runs"
        )
    )
    op.execute(
        sa.text("ALTER TABLE tenant_flow_sandbox_runs NO FORCE ROW LEVEL SECURITY")
    )
    op.execute(sa.text("ALTER TABLE tenant_flow_sandbox_runs DISABLE ROW LEVEL SECURITY"))
    op.drop_index(
        "ix_tenant_flow_sandbox_runs_tenant_created",
        table_name="tenant_flow_sandbox_runs",
    )
    op.drop_table("tenant_flow_sandbox_runs")

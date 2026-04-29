"""tenant_flow_drafts: rascunhos de fluxo por tenant (Story 5.1).

Revision ID: 018
Revises: 017
Create Date: 2026-04-29

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "018"
down_revision: Union[str, None] = "017"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenant_flow_drafts",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("definition", JSONB(), nullable=False),
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
        "ix_tenant_flow_drafts_tenant_id",
        "tenant_flow_drafts",
        ["tenant_id"],
    )
    op.execute(sa.text("ALTER TABLE tenant_flow_drafts ENABLE ROW LEVEL SECURITY"))
    op.execute(sa.text("ALTER TABLE tenant_flow_drafts FORCE ROW LEVEL SECURITY"))
    op.execute(
        sa.text(
            """
            CREATE POLICY tenant_flow_drafts_isolation ON tenant_flow_drafts
            FOR ALL
            USING (tenant_id::text = current_setting('app.tenant_id', true))
            WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true))
            """
        )
    )
    op.execute(
        sa.text(
            "GRANT SELECT, INSERT, UPDATE, DELETE ON tenant_flow_drafts TO app_runtime"
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DROP POLICY IF EXISTS tenant_flow_drafts_isolation ON tenant_flow_drafts"
        )
    )
    op.execute(sa.text("ALTER TABLE tenant_flow_drafts NO FORCE ROW LEVEL SECURITY"))
    op.execute(sa.text("ALTER TABLE tenant_flow_drafts DISABLE ROW LEVEL SECURITY"))
    op.drop_index("ix_tenant_flow_drafts_tenant_id", table_name="tenant_flow_drafts")
    op.drop_table("tenant_flow_drafts")

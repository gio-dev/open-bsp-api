"""tenant_sandbox_webhook_deliveries (Story 7.3 webhook delivery log + RLS).

Revision ID: 025
Revises: 024
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "025"
down_revision: Union[str, None] = "024"
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenant_sandbox_webhook_deliveries",
        sa.Column(
            "id",
            sa.Uuid(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("request_id", sa.String(256), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column(
            "enqueued",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "deduplicated",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "skipped",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.CheckConstraint(
            "status IN ('accepted')",
            name="ck_tenant_sandbox_webhook_deliveries_status",
        ),
    )
    op.create_index(
        "ix_tenant_sandbox_webhook_deliveries_tenant_created",
        "tenant_sandbox_webhook_deliveries",
        ["tenant_id", "created_at"],
        postgresql_ops={"created_at": "DESC"},
    )
    op.execute(
        sa.text(
            "ALTER TABLE tenant_sandbox_webhook_deliveries ENABLE ROW LEVEL SECURITY",
        ),
    )
    op.execute(
        sa.text(
            "ALTER TABLE tenant_sandbox_webhook_deliveries FORCE ROW LEVEL SECURITY",
        ),
    )
    op.execute(
        sa.text(
            """
            CREATE POLICY tenant_sandbox_webhook_deliveries_isolation
            ON tenant_sandbox_webhook_deliveries
            FOR ALL
            USING (
                tenant_id::text = current_setting('app.tenant_id', true)
            )
            WITH CHECK (
                tenant_id::text = current_setting('app.tenant_id', true)
            )
            """
        ),
    )
    op.execute(
        sa.text(
            "GRANT SELECT, INSERT, UPDATE, DELETE "
            "ON tenant_sandbox_webhook_deliveries TO app_runtime"
        ),
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DROP POLICY IF EXISTS tenant_sandbox_webhook_deliveries_isolation "
            "ON tenant_sandbox_webhook_deliveries"
        ),
    )
    op.execute(
        sa.text(
            "ALTER TABLE tenant_sandbox_webhook_deliveries NO FORCE ROW LEVEL SECURITY",
        ),
    )
    op.execute(
        sa.text(
            "ALTER TABLE tenant_sandbox_webhook_deliveries DISABLE ROW LEVEL SECURITY",
        ),
    )
    op.drop_index(
        "ix_tenant_sandbox_webhook_deliveries_tenant_created",
        table_name="tenant_sandbox_webhook_deliveries",
    )
    op.drop_table("tenant_sandbox_webhook_deliveries")

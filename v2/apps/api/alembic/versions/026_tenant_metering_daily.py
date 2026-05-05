"""tenant_metering_daily (Story 8.1 metering MVP + RLS).

Revision ID: 026
Revises: 025
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "026"
down_revision: Union[str, None] = "025"
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenant_metering_daily",
        sa.Column(
            "id",
            sa.Uuid(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("bucket_date", sa.Date(), nullable=False),
        sa.Column("metric_key", sa.String(64), nullable=False),
        sa.Column(
            "count",
            sa.BigInteger(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "tenant_id",
            "bucket_date",
            "metric_key",
            name="uq_tenant_metering_daily_tenant_bucket_metric",
        ),
    )
    op.create_index(
        "ix_tenant_metering_daily_tenant_bucket",
        "tenant_metering_daily",
        ["tenant_id", "bucket_date"],
    )
    op.execute(
        sa.text("ALTER TABLE tenant_metering_daily ENABLE ROW LEVEL SECURITY"),
    )
    op.execute(
        sa.text("ALTER TABLE tenant_metering_daily FORCE ROW LEVEL SECURITY"),
    )
    op.execute(
        sa.text(
            """
            CREATE POLICY tenant_metering_daily_isolation ON tenant_metering_daily
            FOR ALL
            USING (tenant_id::text = current_setting('app.tenant_id', true))
            WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true))
            """
        ),
    )
    op.execute(
        sa.text(
            "GRANT SELECT, INSERT, UPDATE, DELETE ON tenant_metering_daily "
            "TO app_runtime"
        ),
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DROP POLICY IF EXISTS tenant_metering_daily_isolation "
            "ON tenant_metering_daily",
        ),
    )
    op.execute(
        sa.text(
            "ALTER TABLE tenant_metering_daily NO FORCE ROW LEVEL SECURITY",
        ),
    )
    op.execute(
        sa.text("ALTER TABLE tenant_metering_daily DISABLE ROW LEVEL SECURITY"),
    )
    op.drop_index(
        "ix_tenant_metering_daily_tenant_bucket",
        table_name="tenant_metering_daily",
    )
    op.drop_table("tenant_metering_daily")

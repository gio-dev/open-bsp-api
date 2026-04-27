"""webhook_verify_secrets + RLS (Story 2.4)

Revision ID: 008
Revises: 007
Create Date: 2026-04-27

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "webhook_verify_secrets",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("secret_hash", sa.String(255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("invalid_after", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_webhook_verify_secrets_tenant_id",
        "webhook_verify_secrets",
        ["tenant_id"],
    )

    op.execute(sa.text("ALTER TABLE webhook_verify_secrets ENABLE ROW LEVEL SECURITY"))
    op.execute(sa.text("ALTER TABLE webhook_verify_secrets FORCE ROW LEVEL SECURITY"))
    op.execute(
        sa.text("""
        CREATE POLICY webhook_verify_secrets_isolation ON webhook_verify_secrets
        FOR ALL
        USING (tenant_id::text = current_setting('app.tenant_id', true))
        WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true))
        """)
    )
    op.execute(
        sa.text(
            "GRANT SELECT, INSERT, UPDATE, DELETE ON webhook_verify_secrets "
            "TO app_runtime"
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DROP POLICY IF EXISTS webhook_verify_secrets_isolation "
            "ON webhook_verify_secrets"
        )
    )
    op.execute(
        sa.text("ALTER TABLE webhook_verify_secrets NO FORCE ROW LEVEL SECURITY")
    )
    op.execute(sa.text("ALTER TABLE webhook_verify_secrets DISABLE ROW LEVEL SECURITY"))
    op.drop_index(
        "ix_webhook_verify_secrets_tenant_id", table_name="webhook_verify_secrets"
    )
    op.drop_table("webhook_verify_secrets")

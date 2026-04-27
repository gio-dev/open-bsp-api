"""api_keys + RLS (Story 2.3)

Revision ID: 006
Revises: 005
Create Date: 2026-04-27

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "api_keys",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("key_prefix", sa.String(48), nullable=False),
        sa.Column("secret_hash", sa.String(255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "tenant_id",
            "key_prefix",
            name="uq_api_keys_tenant_prefix",
        ),
    )
    op.create_index("ix_api_keys_tenant_id", "api_keys", ["tenant_id"])

    op.execute(sa.text("ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY"))
    op.execute(sa.text("ALTER TABLE api_keys FORCE ROW LEVEL SECURITY"))
    op.execute(
        sa.text("""
        CREATE POLICY api_keys_isolation ON api_keys
        FOR ALL
        USING (tenant_id::text = current_setting('app.tenant_id', true))
        WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true))
        """)
    )
    op.execute(
        sa.text("GRANT SELECT, INSERT, UPDATE, DELETE ON api_keys TO app_runtime")
    )


def downgrade() -> None:
    op.execute(sa.text("DROP POLICY IF EXISTS api_keys_isolation ON api_keys"))
    op.execute(sa.text("ALTER TABLE api_keys NO FORCE ROW LEVEL SECURITY"))
    op.execute(sa.text("ALTER TABLE api_keys DISABLE ROW LEVEL SECURITY"))
    op.drop_index("ix_api_keys_tenant_id", table_name="api_keys")
    op.drop_table("api_keys")

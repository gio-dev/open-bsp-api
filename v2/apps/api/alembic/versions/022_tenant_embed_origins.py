"""tenant_embed_origins: allowlist Origin por tenant (Story 6.1).

Revision ID: 022
Revises: 021
Create Date: 2026-04-30

Valor normalizado scheme://host[:port] em minusculas (sem path).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "022"
down_revision: Union[str, None] = "021"
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenant_embed_origins",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("origin", sa.String(512), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "origin",
            name="uq_tenant_embed_origin",
        ),
    )
    op.create_index(
        "ix_tenant_embed_origins_tenant_id",
        "tenant_embed_origins",
        ["tenant_id"],
    )
    op.execute(sa.text("ALTER TABLE tenant_embed_origins ENABLE ROW LEVEL SECURITY"))
    op.execute(sa.text("ALTER TABLE tenant_embed_origins FORCE ROW LEVEL SECURITY"))
    op.execute(
        sa.text(
            """
            CREATE POLICY tenant_embed_origins_isolation ON tenant_embed_origins
            FOR ALL
            USING (tenant_id::text = current_setting('app.tenant_id', true))
            WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true))
            """
        )
    )
    op.execute(
        sa.text(
            "GRANT SELECT, INSERT, UPDATE, DELETE ON tenant_embed_origins "
            "TO app_runtime"
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DROP POLICY IF EXISTS tenant_embed_origins_isolation "
            "ON tenant_embed_origins"
        )
    )
    op.execute(sa.text("ALTER TABLE tenant_embed_origins NO FORCE ROW LEVEL SECURITY"))
    op.execute(sa.text("ALTER TABLE tenant_embed_origins DISABLE ROW LEVEL SECURITY"))
    op.drop_index(
        "ix_tenant_embed_origins_tenant_id",
        table_name="tenant_embed_origins",
    )
    op.drop_table("tenant_embed_origins")

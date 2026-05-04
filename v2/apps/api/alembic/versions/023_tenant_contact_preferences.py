"""tenant_contact_preferences: opt-in granular por contacto (Story 6.3).

Revision ID: 023
Revises: 022
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "023"
down_revision: Union[str, None] = "022"
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenant_contact_preferences",
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("contact_id", sa.String(128), nullable=False),
        sa.Column(
            "marketing_opt_in",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "transactional_allowed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "disclosure_copy_slug",
            sa.String(128),
            nullable=False,
            server_default=sa.text("'baseline-v1'"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "tenant_id",
            "contact_id",
            name="pk_tenant_contact_preferences",
        ),
    )
    op.create_index(
        "ix_tcp_tenant_contact",
        "tenant_contact_preferences",
        ["tenant_id", "contact_id"],
    )
    op.execute(
        sa.text("ALTER TABLE tenant_contact_preferences ENABLE ROW LEVEL SECURITY"),
    )
    op.execute(
        sa.text("ALTER TABLE tenant_contact_preferences FORCE ROW LEVEL SECURITY"),
    )
    op.execute(
        sa.text(
            """
            CREATE POLICY tenant_contact_preferences_isolation
              ON tenant_contact_preferences
              FOR ALL
              USING (tenant_id::text = current_setting('app.tenant_id', true))
              WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true))
            """
        ),
    )
    op.execute(
        sa.text(
            "GRANT SELECT, INSERT, UPDATE, DELETE ON tenant_contact_preferences "
            "TO app_runtime"
        ),
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DROP POLICY IF EXISTS tenant_contact_preferences_isolation "
            "ON tenant_contact_preferences"
        ),
    )
    op.execute(
        sa.text("ALTER TABLE tenant_contact_preferences NO FORCE ROW LEVEL SECURITY"),
    )
    op.execute(
        sa.text("ALTER TABLE tenant_contact_preferences DISABLE ROW LEVEL SECURITY"),
    )
    op.drop_index("ix_tcp_tenant_contact", table_name="tenant_contact_preferences")
    op.drop_table("tenant_contact_preferences")

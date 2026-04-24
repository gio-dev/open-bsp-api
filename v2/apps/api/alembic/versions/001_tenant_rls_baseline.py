"""tenant + tenant_settings_stub + RLS + app_runtime role

Revision ID: 001
Revises:
Create Date: 2026-04-24

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Credencial em texto: apenas ambientes descartaveis (dev/CI). Em producao,
    # criar/alterar o role fora desta revisao (secret manager) e alinhar DATABASE_URL.
    op.execute(
        sa.text("""
        DO $$ BEGIN
          CREATE ROLE app_runtime LOGIN PASSWORD 'app_runtime_dev_only';
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
        """)
    )

    op.create_table(
        "tenants",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "tenant_settings_stub",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column(
            "display_name",
            sa.String(255),
            server_default=sa.text("''"),
            nullable=False,
        ),
        sa.Column(
            "timezone",
            sa.String(64),
            server_default=sa.text("'UTC'"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("tenant_id", name="uq_tenant_settings_stub_tenant_id"),
    )

    op.execute(sa.text("ALTER TABLE tenants ENABLE ROW LEVEL SECURITY"))
    op.execute(sa.text("ALTER TABLE tenants FORCE ROW LEVEL SECURITY"))
    op.execute(
        sa.text("""
        CREATE POLICY tenants_isolation ON tenants
        FOR ALL
        USING (id::text = current_setting('app.tenant_id', true))
        WITH CHECK (id::text = current_setting('app.tenant_id', true))
        """)
    )

    op.execute(sa.text("ALTER TABLE tenant_settings_stub ENABLE ROW LEVEL SECURITY"))
    op.execute(sa.text("ALTER TABLE tenant_settings_stub FORCE ROW LEVEL SECURITY"))
    op.execute(
        sa.text("""
        CREATE POLICY tenant_settings_stub_isolation ON tenant_settings_stub
        FOR ALL
        USING (tenant_id::text = current_setting('app.tenant_id', true))
        WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true))
        """)
    )

    op.execute(sa.text("GRANT USAGE ON SCHEMA public TO app_runtime"))
    op.execute(
        sa.text("GRANT SELECT, INSERT, UPDATE, DELETE ON tenants TO app_runtime")
    )
    op.execute(
        sa.text(
            "GRANT SELECT, INSERT, UPDATE, DELETE ON tenant_settings_stub "
            "TO app_runtime"
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DROP POLICY IF EXISTS tenant_settings_stub_isolation "
            "ON tenant_settings_stub"
        )
    )
    op.execute(sa.text("ALTER TABLE tenant_settings_stub NO FORCE ROW LEVEL SECURITY"))
    op.execute(sa.text("ALTER TABLE tenant_settings_stub DISABLE ROW LEVEL SECURITY"))
    op.execute(sa.text("DROP POLICY IF EXISTS tenants_isolation ON tenants"))
    op.execute(sa.text("ALTER TABLE tenants NO FORCE ROW LEVEL SECURITY"))
    op.execute(sa.text("ALTER TABLE tenants DISABLE ROW LEVEL SECURITY"))
    op.drop_table("tenant_settings_stub")
    op.drop_table("tenants")
    op.execute(sa.text("DROP ROLE IF EXISTS app_runtime"))

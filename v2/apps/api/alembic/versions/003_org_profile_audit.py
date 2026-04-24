"""tenant_settings operational_email + audit_events RLS

Revision ID: 003
Revises: 002
Create Date: 2026-04-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tenant_settings_stub",
        sa.Column(
            "operational_email",
            sa.String(320),
            server_default=sa.text("''"),
            nullable=False,
        ),
    )

    op.create_table(
        "audit_events",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("actor_user_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("resource_type", sa.String(64), nullable=False),
        sa.Column("summary", sa.String(1024), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            ondelete="CASCADE",
        ),
    )

    op.execute(sa.text("ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY"))
    op.execute(sa.text("ALTER TABLE audit_events FORCE ROW LEVEL SECURITY"))
    op.execute(
        sa.text("""
        CREATE POLICY audit_events_isolation ON audit_events
        FOR ALL
        USING (tenant_id::text = current_setting('app.tenant_id', true))
        WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true))
        """)
    )

    op.execute(sa.text("GRANT SELECT, INSERT ON audit_events TO app_runtime"))


def downgrade() -> None:
    op.execute(sa.text("DROP POLICY IF EXISTS audit_events_isolation ON audit_events"))
    op.execute(sa.text("ALTER TABLE audit_events NO FORCE ROW LEVEL SECURITY"))
    op.execute(sa.text("ALTER TABLE audit_events DISABLE ROW LEVEL SECURITY"))
    op.drop_table("audit_events")
    op.drop_column("tenant_settings_stub", "operational_email")

"""waba_phone_numbers + RLS

Revision ID: 002
Revises: 001
Create Date: 2026-04-24

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "waba_phone_numbers",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("waba_id", sa.String(128), nullable=False),
        sa.Column("phone_number_id", sa.String(128), nullable=False),
        sa.Column("display_phone_number", sa.String(64), nullable=False),
        sa.Column("environment", sa.String(32), nullable=False),
        sa.Column(
            "status",
            sa.String(32),
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
    )

    op.execute(sa.text("ALTER TABLE waba_phone_numbers ENABLE ROW LEVEL SECURITY"))
    op.execute(sa.text("ALTER TABLE waba_phone_numbers FORCE ROW LEVEL SECURITY"))
    op.execute(
        sa.text("""
        CREATE POLICY waba_phone_numbers_isolation ON waba_phone_numbers
        FOR ALL
        USING (tenant_id::text = current_setting('app.tenant_id', true))
        WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true))
        """)
    )
    op.execute(
        sa.text(
            "GRANT SELECT, INSERT, UPDATE, DELETE ON waba_phone_numbers TO app_runtime"
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DROP POLICY IF EXISTS waba_phone_numbers_isolation ON waba_phone_numbers"
        )
    )
    op.execute(sa.text("ALTER TABLE waba_phone_numbers NO FORCE ROW LEVEL SECURITY"))
    op.execute(sa.text("ALTER TABLE waba_phone_numbers DISABLE ROW LEVEL SECURITY"))
    op.drop_table("waba_phone_numbers")

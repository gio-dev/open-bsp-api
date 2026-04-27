"""GRANT app_runtime em console_users / tenant_memberships (OIDC platform_session)

Revision ID: 007
Revises: 006
Create Date: 2026-04-27

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text("GRANT SELECT, INSERT, UPDATE, DELETE ON console_users TO app_runtime")
    )
    op.execute(
        sa.text(
            "GRANT SELECT, INSERT, UPDATE, DELETE ON tenant_memberships TO app_runtime"
        )
    )


def downgrade() -> None:
    op.execute(sa.text("REVOKE ALL PRIVILEGES ON tenant_memberships FROM app_runtime"))
    op.execute(sa.text("REVOKE ALL PRIVILEGES ON console_users FROM app_runtime"))

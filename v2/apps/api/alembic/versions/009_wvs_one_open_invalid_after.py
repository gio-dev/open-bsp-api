"""No max um segredo "aberto" (invalid_after NULL) por tenant. Story 2.4 (hardening).

Revision ID: 009
Revises: 008
Create Date: 2026-04-24

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            CREATE UNIQUE INDEX ix_uq_wvs_tenant_one_open
            ON webhook_verify_secrets (tenant_id)
            WHERE (invalid_after IS NULL)
            """
        )
    )


def downgrade() -> None:
    op.execute(sa.text("DROP INDEX IF EXISTS ix_uq_wvs_tenant_one_open"))

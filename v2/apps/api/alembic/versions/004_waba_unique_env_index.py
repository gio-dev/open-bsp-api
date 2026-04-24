"""waba_phone_numbers UNIQUE (tenant, phone_number_id, env) + index

Revision ID: 004
Revises: 003
Create Date: 2026-04-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ATDD repetido pode deixar duplicados; manter a linha com menor id por chave.
    op.execute(
        sa.text("""
        DELETE FROM waba_phone_numbers w
        WHERE EXISTS (
          SELECT 1 FROM waba_phone_numbers w2
          WHERE w2.tenant_id = w.tenant_id
            AND w2.phone_number_id = w.phone_number_id
            AND w2.environment = w.environment
            AND w2.id < w.id
        )
        """)
    )

    op.create_unique_constraint(
        "uq_waba_phone_tenant_phone_env",
        "waba_phone_numbers",
        ["tenant_id", "phone_number_id", "environment"],
    )
    op.create_index(
        "ix_waba_phone_numbers_tenant_environment",
        "waba_phone_numbers",
        ["tenant_id", "environment"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_waba_phone_numbers_tenant_environment",
        table_name="waba_phone_numbers",
    )
    op.drop_constraint(
        "uq_waba_phone_tenant_phone_env",
        "waba_phone_numbers",
        type_="unique",
    )

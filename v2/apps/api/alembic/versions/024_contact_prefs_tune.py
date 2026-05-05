"""Drop redundant index; marketing consent timestamp (Story 6.3 remediacao).

Revision ID: 024
Revises: 023
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "024"
down_revision: Union[str, None] = "023"
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_tcp_tenant_contact", table_name="tenant_contact_preferences")
    op.add_column(
        "tenant_contact_preferences",
        sa.Column(
            "marketing_consent_recorded_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("tenant_contact_preferences", "marketing_consent_recorded_at")
    op.create_index(
        "ix_tcp_tenant_contact",
        "tenant_contact_preferences",
        ["tenant_id", "contact_id"],
    )

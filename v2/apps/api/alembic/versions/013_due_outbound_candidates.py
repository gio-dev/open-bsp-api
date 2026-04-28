"""due_outbound_candidates (SECURITY DEFINER) para sweep cross-tenant. Story 3.2.

Revision ID: 013
Revises: 012
Create Date: 2026-04-28

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "013"
down_revision: Union[str, None] = "012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text("""
        CREATE OR REPLACE FUNCTION public.due_outbound_candidates(p_limit integer)
        RETURNS TABLE(message_id uuid, p_tenant_id uuid)
        LANGUAGE sql
        STABLE
        SECURITY DEFINER
        SET search_path = public
        AS $fn$
          SELECT m.id AS message_id, m.tenant_id AS p_tenant_id
          FROM outbound_whatsapp_messages m
          WHERE m.status IN ('queued', 'rate_limited')
            AND (
              m.next_attempt_at IS NULL
              OR m.next_attempt_at <= now()
            )
          ORDER BY m.created_at ASC
          LIMIT p_limit;
        $fn$;
        """)
    )
    op.execute(
        sa.text(
            "REVOKE ALL ON FUNCTION public.due_outbound_candidates(integer) FROM PUBLIC"
        )
    )
    op.execute(
        sa.text(
            "GRANT EXECUTE ON FUNCTION public.due_outbound_candidates(integer) "
            "TO app_runtime"
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text("DROP FUNCTION IF EXISTS public.due_outbound_candidates(integer)")
    )

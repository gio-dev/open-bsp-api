"""resolve_waba_tenant returns (tenant_id, resolve_status) for ambiguous WABA handling.

Revision ID: 011
Revises: 010
Create Date: 2026-04-28

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "011"
down_revision: Union[str, None] = "010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text("DROP FUNCTION IF EXISTS public.resolve_waba_tenant(text, text)")
    )
    op.execute(
        sa.text("""
        CREATE OR REPLACE FUNCTION public.resolve_waba_tenant(
          p_waba_id text,
          p_phone_number_id text
        ) RETURNS TABLE(tenant_id uuid, resolve_status text)
        LANGUAGE sql
        STABLE
        SECURITY DEFINER
        SET search_path = public
        AS $fn$
          WITH filtered AS (
            SELECT w.tenant_id
            FROM waba_phone_numbers w
            WHERE w.waba_id = p_waba_id
              AND (
                p_phone_number_id IS NULL
                OR length(trim(p_phone_number_id)) = 0
                OR w.phone_number_id = p_phone_number_id
              )
          ),
          ndist AS (
            SELECT
              COUNT(DISTINCT f.tenant_id) AS c,
              MIN(f.tenant_id::text)::uuid AS tid
            FROM filtered f
          )
          SELECT
            CASE WHEN n.c = 1 THEN n.tid ELSE NULL END,
            CASE
              WHEN n.c = 0 THEN 'none'
              WHEN n.c = 1 THEN 'ok'
              ELSE 'ambiguous'
            END::text
          FROM ndist n;
        $fn$;
        """)
    )
    op.execute(
        sa.text(
            "REVOKE ALL ON FUNCTION public.resolve_waba_tenant(text, text) FROM PUBLIC"
        )
    )
    op.execute(
        sa.text(
            "GRANT EXECUTE ON FUNCTION public.resolve_waba_tenant(text, text) "
            "TO app_runtime"
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text("DROP FUNCTION IF EXISTS public.resolve_waba_tenant(text, text)")
    )
    op.execute(
        sa.text("""
        CREATE OR REPLACE FUNCTION public.resolve_waba_tenant(
          p_waba_id text,
          p_phone_number_id text
        ) RETURNS uuid
        LANGUAGE sql
        STABLE
        SECURITY DEFINER
        SET search_path = public
        AS $fn$
          SELECT w.tenant_id
          FROM waba_phone_numbers w
          WHERE w.waba_id = p_waba_id
            AND (
              p_phone_number_id IS NULL
              OR length(trim(p_phone_number_id)) = 0
              OR w.phone_number_id = p_phone_number_id
            )
          ORDER BY
            CASE
              WHEN p_phone_number_id IS NOT NULL
                AND length(trim(p_phone_number_id)) > 0
                AND w.phone_number_id = p_phone_number_id
              THEN 0
              ELSE 1
            END,
            w.created_at ASC
          LIMIT 1;
        $fn$;
        """)
    )
    op.execute(
        sa.text(
            "REVOKE ALL ON FUNCTION public.resolve_waba_tenant(text, text) FROM PUBLIC"
        )
    )
    op.execute(
        sa.text(
            "GRANT EXECUTE ON FUNCTION public.resolve_waba_tenant(text, text) "
            "TO app_runtime"
        )
    )

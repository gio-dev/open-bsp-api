"""Allowlist de origens embed por tenant (Story 6.1)."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import TenantEmbedOrigin


async def tenant_has_embed_origin(
    session: AsyncSession,
    tenant_id: UUID,
    normalized_origin: str,
) -> bool:
    """True se `normalized_origin` esta gravada para o tenant."""
    q = select(
        exists().where(
            TenantEmbedOrigin.tenant_id == tenant_id,
            TenantEmbedOrigin.origin == normalized_origin,
        ),
    )
    res = await session.execute(q)
    return bool(res.scalar())

"""Utilizador consola e memberships (sem RLS de tenant)."""

from __future__ import annotations

import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ConsoleUser, TenantMembership


async def upsert_console_user(
    session: AsyncSession, oidc_sub: str, email: str
) -> ConsoleUser:
    row = await session.scalar(
        select(ConsoleUser).where(ConsoleUser.oidc_sub == oidc_sub)
    )
    if row:
        row.email = email
        await session.flush()
        return row
    u = ConsoleUser(
        id=uuid.uuid4(),
        oidc_sub=oidc_sub,
        email=email,
    )
    session.add(u)
    await session.flush()
    return u


async def all_memberships_for_user(
    session: AsyncSession, user_id: UUID
) -> list[TenantMembership]:
    q = select(TenantMembership).where(TenantMembership.user_id == user_id)
    res = await session.execute(q)
    return list(res.scalars().all())


async def membership_for_user_tenant(
    session: AsyncSession,
    user_id: UUID,
    tenant_id: UUID,
) -> TenantMembership | None:
    return await session.scalar(
        select(TenantMembership).where(
            TenantMembership.user_id == user_id,
            TenantMembership.tenant_id == tenant_id,
        )
    )


async def org_admin_memberships(
    session: AsyncSession, user_id: UUID
) -> list[TenantMembership]:
    q = select(TenantMembership).where(
        TenantMembership.user_id == user_id,
        TenantMembership.role == "org_admin",
    )
    res = await session.execute(q)
    return list(res.scalars().all())


def resolve_active_tenant_id(
    memberships: list[TenantMembership],
    claim_tid: UUID | None,
) -> UUID:
    if claim_tid is not None:
        if any(m.tenant_id == claim_tid for m in memberships):
            return claim_tid
        raise ValueError("tenant_claim_not_in_memberships")
    if not memberships:
        raise ValueError("no_membership")
    if len(memberships) == 1:
        return memberships[0].tenant_id
    ordered = sorted(memberships, key=lambda m: str(m.tenant_id))
    return ordered[0].tenant_id

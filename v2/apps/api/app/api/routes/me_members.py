"""Gestao de membros do tenant (Story 2.2)."""

from __future__ import annotations

import uuid
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import CanonicalErrorResponse, CanonicalValidationErrorResponse
from app.db.models import AuditEvent, ConsoleUser, TenantMembership
from app.db.session import platform_session, tenant_session
from app.tenancy.deps import TenantUserContext, console_org_admin_context
from app.tenancy.rbac import VALID_TENANT_ROLES

router = APIRouter(tags=["members"])

_MEMBER_RESPONSES = {
    401: {"model": CanonicalErrorResponse},
    403: {"model": CanonicalErrorResponse},
    404: {"model": CanonicalErrorResponse},
    422: {"model": CanonicalValidationErrorResponse},
    503: {"model": CanonicalErrorResponse},
}


class TenantMemberItem(BaseModel):
    user_id: UUID
    email: str
    role: str


class TenantMemberListResponse(BaseModel):
    items: list[TenantMemberItem]


class TenantMemberPatch(BaseModel):
    role: str = Field(min_length=1, max_length=64)

    @field_validator("role")
    @classmethod
    def role_known(cls, v: str) -> str:
        if v not in VALID_TENANT_ROLES:
            raise ValueError("role must be a known tenant role")
        return v


@router.get(
    "/me/members",
    response_model=TenantMemberListResponse,
    responses=_MEMBER_RESPONSES,
)
async def list_tenant_members(
    ctx: Annotated[TenantUserContext, Depends(console_org_admin_context)],
) -> TenantMemberListResponse:
    settings = get_settings()
    if not settings.database_url:
        raise HTTPException(status_code=503, detail="database unavailable")

    async with platform_session() as session:
        q = (
            select(TenantMembership, ConsoleUser)
            .join(ConsoleUser, ConsoleUser.id == TenantMembership.user_id)
            .where(TenantMembership.tenant_id == ctx.tenant_id)
            .order_by(TenantMembership.role, TenantMembership.user_id)
        )
        res = await session.execute(q)
        rows = res.all()

    items = [
        TenantMemberItem(user_id=m.user_id, email=u.email, role=m.role)
        for m, u in rows
    ]
    return TenantMemberListResponse(items=items)


async def _count_org_admins(session: AsyncSession, tenant_id: UUID) -> int:
    q = select(func.count(TenantMembership.id)).where(
        TenantMembership.tenant_id == tenant_id,
        TenantMembership.role == "org_admin",
    )
    n = await session.scalar(q)
    return int(n or 0)


@router.patch(
    "/me/members/{user_id}",
    response_model=TenantMemberItem,
    responses=_MEMBER_RESPONSES,
)
async def patch_tenant_member(
    user_id: UUID,
    body: TenantMemberPatch,
    ctx: Annotated[TenantUserContext, Depends(console_org_admin_context)],
) -> TenantMemberItem:
    settings = get_settings()
    if not settings.database_url:
        raise HTTPException(status_code=503, detail="database unavailable")

    # Uma so transaccao: membership (sem RLS) + audit_events (RLS) com o mesmo GUC.
    async with tenant_session(ctx.tenant_id) as session:
        m = await session.scalar(
            select(TenantMembership).where(
                TenantMembership.tenant_id == ctx.tenant_id,
                TenantMembership.user_id == user_id,
            )
        )
        if m is None:
            raise HTTPException(status_code=404, detail="member not found")

        if m.role == "org_admin" and body.role != "org_admin":
            n = await _count_org_admins(session, ctx.tenant_id)
            if n <= 1:
                raise HTTPException(
                    status_code=403,
                    detail="cannot remove last org_admin",
                )

        old_role = m.role
        m.role = body.role
        session.add(m)
        await session.flush()

        u = await session.get(ConsoleUser, user_id)
        email = u.email if u else ""

        session.add(
            AuditEvent(
                id=uuid.uuid4(),
                tenant_id=ctx.tenant_id,
                actor_user_id=ctx.actor_user_id,
                resource_type="tenant_membership",
                summary=f"role {old_role!r} -> {body.role!r} user={user_id}",
            )
        )

    return TenantMemberItem(user_id=user_id, email=email, role=body.role)

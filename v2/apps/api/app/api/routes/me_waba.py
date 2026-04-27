"""WABA phone numbers (Story 1.4): environments, pagination, status lifecycle."""

from __future__ import annotations

import uuid
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.core.errors import CanonicalErrorResponse
from app.db.models_waba import WabaPhoneNumber
from app.db.session import tenant_session
from app.tenancy.deps import (
    TenantUserContext,
    console_tenant_user_context,
    console_waba_write_context,
)

router = APIRouter(tags=["waba"])

_ENVIRONMENTS = frozenset({"development", "staging", "production"})
_WABA_ERROR_RESPONSES = {
    403: {
        "model": CanonicalErrorResponse,
        "description": (
            "Acesso negado: sem contexto de tenant/sessao, ou papel insuficiente. "
            "Post/PATCH de numeros WABA exigem org_admin (RBAC Story 2.2); "
            "GET lista com qualquer membro do tenant."
        ),
    },
    404: {
        "model": CanonicalErrorResponse,
        "description": "Recurso nao encontrado para o tenant atual.",
    },
    409: {
        "model": CanonicalErrorResponse,
        "description": "Conflito (ex.: UNIQUE tenant/phone_number_id/environment).",
    },
    422: {
        "model": CanonicalErrorResponse,
        "description": "Validacao (ambiente, estado, limites).",
    },
    503: {
        "model": CanonicalErrorResponse,
        "description": "Base de dados indisponivel.",
    },
}


class WabaPhoneCreate(BaseModel):
    waba_id: str = Field(max_length=128)
    phone_number_id: str = Field(max_length=128)
    display_phone_number: str = Field(max_length=64)
    environment: str = Field(default="production", max_length=32)

    @field_validator("environment")
    @classmethod
    def environment_ok(cls, v: str) -> str:
        if v not in _ENVIRONMENTS:
            raise ValueError("environment must be development, staging, or production")
        return v


class WabaPhonePatch(BaseModel):
    status: Literal["active", "pending", "suspended"] | None = None
    display_phone_number: str | None = Field(default=None, max_length=64)


class WabaPhoneItem(BaseModel):
    id: str
    waba_id: str
    phone_number_id: str
    display_phone_number: str
    environment: str
    status: str


class WabaPhoneListResponse(BaseModel):
    items: list[WabaPhoneItem]
    limit: int
    next_cursor: str | None = None


def _resolve_list_environment(
    query_env: str | None,
    header_env: str | None,
) -> str:
    raw = (query_env or header_env or "production").strip()
    if raw not in _ENVIRONMENTS:
        raise HTTPException(
            status_code=422,
            detail="environment must be development, staging, or production",
        )
    return raw


@router.post(
    "/me/waba-phone-numbers",
    status_code=201,
    response_model=WabaPhoneItem,
    responses=_WABA_ERROR_RESPONSES,
)
async def create_waba_phone(
    body: WabaPhoneCreate,
    ctx: Annotated[TenantUserContext, Depends(console_waba_write_context)],
) -> WabaPhoneItem:
    settings = get_settings()
    if not settings.database_url:
        raise HTTPException(status_code=503, detail="database unavailable")

    row = WabaPhoneNumber(
        id=uuid.uuid4(),
        tenant_id=ctx.tenant_id,
        waba_id=body.waba_id,
        phone_number_id=body.phone_number_id,
        display_phone_number=body.display_phone_number,
        environment=body.environment,
        status="pending",
    )
    try:
        async with tenant_session(ctx.tenant_id) as session:
            session.add(row)
            await session.flush()
            return WabaPhoneItem(
                id=str(row.id),
                waba_id=row.waba_id,
                phone_number_id=row.phone_number_id,
                display_phone_number=row.display_phone_number,
                environment=row.environment,
                status=row.status,
            )
    except IntegrityError as e:
        raise HTTPException(
            status_code=409,
            detail="waba phone number already exists for this environment",
        ) from e


@router.get(
    "/me/waba-phone-numbers",
    response_model=WabaPhoneListResponse,
    responses=_WABA_ERROR_RESPONSES,
)
async def list_waba_phones(
    ctx: Annotated[TenantUserContext, Depends(console_tenant_user_context)],
    environment: str | None = Query(
        default=None,
        max_length=32,
        description="Filter: development | staging | production (default: production).",
    ),
    x_environment: str | None = Header(default=None, alias="X-Environment"),
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
        description="Page size (max 100).",
    ),
    cursor: UUID | None = Query(
        default=None,
        description="Pagination cursor (id of last item from previous page).",
    ),
) -> WabaPhoneListResponse:
    settings = get_settings()
    if not settings.database_url:
        raise HTTPException(status_code=503, detail="database unavailable")

    env = _resolve_list_environment(environment, x_environment)

    async with tenant_session(ctx.tenant_id) as session:
        q = (
            select(WabaPhoneNumber)
            .where(
                WabaPhoneNumber.tenant_id == ctx.tenant_id,
                WabaPhoneNumber.environment == env,
            )
            .order_by(WabaPhoneNumber.id.asc())
        )
        if cursor is not None:
            q = q.where(WabaPhoneNumber.id > cursor)
        q = q.limit(limit + 1)
        res = await session.execute(q)
        rows = list(res.scalars().all())

    has_more = len(rows) > limit
    page = rows[:limit]
    next_cursor = str(page[-1].id) if has_more and page else None

    items = [
        WabaPhoneItem(
            id=str(r.id),
            waba_id=r.waba_id,
            phone_number_id=r.phone_number_id,
            display_phone_number=r.display_phone_number,
            environment=r.environment,
            status=r.status,
        )
        for r in page
    ]
    return WabaPhoneListResponse(items=items, limit=limit, next_cursor=next_cursor)


@router.patch(
    "/me/waba-phone-numbers/{row_id}",
    response_model=WabaPhoneItem,
    responses=_WABA_ERROR_RESPONSES,
)
async def patch_waba_phone(
    row_id: UUID,
    body: WabaPhonePatch,
    ctx: Annotated[TenantUserContext, Depends(console_waba_write_context)],
) -> WabaPhoneItem:
    settings = get_settings()
    if not settings.database_url:
        raise HTTPException(status_code=503, detail="database unavailable")

    if body.status is None and body.display_phone_number is None:
        raise HTTPException(status_code=422, detail="no fields to update")

    async with tenant_session(ctx.tenant_id) as session:
        row = await session.scalar(
            select(WabaPhoneNumber).where(
                WabaPhoneNumber.id == row_id,
                WabaPhoneNumber.tenant_id == ctx.tenant_id,
            )
        )
        if row is None:
            raise HTTPException(status_code=404, detail="not found")
        if body.status is not None:
            row.status = body.status
        if body.display_phone_number is not None:
            row.display_phone_number = body.display_phone_number
        session.add(row)
        return WabaPhoneItem(
            id=str(row.id),
            waba_id=row.waba_id,
            phone_number_id=row.phone_number_id,
            display_phone_number=row.display_phone_number,
            environment=row.environment,
            status=row.status,
        )

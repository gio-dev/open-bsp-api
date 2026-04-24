"""Tenant organization profile (Story 1.3): RLS + minimal audit trail."""

import uuid
from typing import Annotated
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select

from app.core.config import get_settings
from app.core.errors import (
    CanonicalErrorResponse,
    CanonicalValidationErrorResponse,
)
from app.db.models import AuditEvent, TenantSettingsStub
from app.db.session import tenant_session
from app.tenancy.deps import (
    TenantUserContext,
    console_org_admin_context,
    console_tenant_user_context,
)

router = APIRouter(tags=["organization"])


class OrganizationResponse(BaseModel):
    display_name: str
    timezone: str
    operational_email: str


class OrganizationPatch(BaseModel):
    display_name: str | None = Field(default=None, max_length=255)
    timezone: str | None = Field(default=None, max_length=64)
    operational_email: str | None = Field(default=None, max_length=320)

    @field_validator("display_name")
    @classmethod
    def display_name_strip(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return v.strip()

    @field_validator("timezone")
    @classmethod
    def timezone_iana(cls, v: str | None) -> str | None:
        if v is None:
            return v
        s = v.strip()
        if not s:
            raise ValueError("timezone cannot be empty")
        try:
            ZoneInfo(s)
        except ZoneInfoNotFoundError as e:
            raise ValueError("timezone must be a valid IANA timezone name") from e
        return s

    @field_validator("operational_email")
    @classmethod
    def operational_email_shape(cls, v: str | None) -> str | None:
        if v is None:
            return v
        s = v.strip()
        if len(s) > 320:
            raise ValueError("operational_email too long")
        if s != "" and "@" not in s:
            raise ValueError("operational_email must contain @")
        return s


_ORG_ERROR_RESPONSES = {
    401: {
        "model": CanonicalErrorResponse,
        "description": (
            "Sessao/autenticacao em falta (OAuth/OIDC apos Epic 2). "
            "Corpo: code=http_401."
        ),
    },
    403: {
        "model": CanonicalErrorResponse,
        "description": (
            "Contexto de tenant em falta, papel insuficiente, ou stub dev desligado. "
            "Corpo: code=http_403."
        ),
    },
    404: {
        "model": CanonicalErrorResponse,
        "description": (
            "Organizacao inexistente para o tenant atual (resposta opaca). "
            "Corpo: code=http_404."
        ),
    },
    422: {
        "model": CanonicalValidationErrorResponse,
        "description": (
            "Validacao de campos: code=validation_error, lista errors (field/message)."
        ),
    },
    503: {
        "model": CanonicalErrorResponse,
        "description": "DATABASE_URL nao configurada ou servico indisponivel.",
    },
}


@router.get(
    "/me/organization",
    response_model=OrganizationResponse,
    responses=_ORG_ERROR_RESPONSES,
)
async def get_me_organization(
    ctx: Annotated[TenantUserContext, Depends(console_tenant_user_context)],
) -> OrganizationResponse:
    settings = get_settings()
    if not settings.database_url:
        raise HTTPException(status_code=503, detail="database unavailable")

    async with tenant_session(ctx.tenant_id) as session:
        row = await session.scalar(
            select(TenantSettingsStub).where(
                TenantSettingsStub.tenant_id == ctx.tenant_id
            )
        )
        if row is None:
            raise HTTPException(status_code=404, detail="organization not found")
        return OrganizationResponse(
            display_name=row.display_name,
            timezone=row.timezone,
            operational_email=row.operational_email,
        )


@router.patch(
    "/me/organization",
    response_model=OrganizationResponse,
    responses=_ORG_ERROR_RESPONSES,
)
async def patch_me_organization(
    body: OrganizationPatch,
    ctx: Annotated[TenantUserContext, Depends(console_org_admin_context)],
) -> OrganizationResponse:
    settings = get_settings()
    if not settings.database_url:
        raise HTTPException(status_code=503, detail="database unavailable")

    async with tenant_session(ctx.tenant_id) as session:
        row = await session.scalar(
            select(TenantSettingsStub).where(
                TenantSettingsStub.tenant_id == ctx.tenant_id
            )
        )
        if row is None:
            raise HTTPException(status_code=404, detail="organization not found")

        changed: list[str] = []
        if body.display_name is not None and body.display_name != row.display_name:
            row.display_name = body.display_name
            changed.append("display_name")
        if body.timezone is not None and body.timezone != row.timezone:
            row.timezone = body.timezone
            changed.append("timezone")
        if (
            body.operational_email is not None
            and body.operational_email != row.operational_email
        ):
            row.operational_email = body.operational_email
            changed.append("operational_email")

        session.add(row)
        if changed:
            session.add(
                AuditEvent(
                    id=uuid.uuid4(),
                    tenant_id=ctx.tenant_id,
                    actor_user_id=ctx.actor_user_id,
                    resource_type="organization_profile",
                    summary="patch:" + ",".join(changed),
                )
            )

        return OrganizationResponse(
            display_name=row.display_name,
            timezone=row.timezone,
            operational_email=row.operational_email,
        )

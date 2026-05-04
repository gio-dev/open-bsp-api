"""Preferencias LGPD/disclosure por contacto (Story 6.3)."""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import select

from app.core.config import get_settings
from app.core.errors import CanonicalErrorResponse
from app.db.models import AuditEvent, TenantContactPreference
from app.db.session import tenant_session
from app.tenancy.deps import TenantUserContext, console_tenant_user_context
from app.tenancy.rbac import CONTACT_PREFERENCE_WRITE_ROLES

router = APIRouter(tags=["contacts"])

_CONTACT_ID_PATTERN = re.compile(r"^[A-Za-z0-9.@_+-]{1,128}$")

_DEFAULT_COPY_SLUG = "baseline-v1"

_RESP = {
    401: {"model": CanonicalErrorResponse},
    403: {"model": CanonicalErrorResponse},
    422: {"model": CanonicalErrorResponse},
    503: {"model": CanonicalErrorResponse},
}


class ContactPreferencesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contact_id: str
    marketing_opt_in: bool = Field(
        description=(
            "True: envios com preference_kind=marketing permitidos (ex. campanhas, "
            "promocoes). Default sem linha: false."
        ),
    )
    transactional_allowed: bool = Field(
        description=(
            "True: envios com preference_kind=transactional permitidos "
            "(confirmacoes, OTP, estado de servico). Default sem linha: true."
        ),
    )
    disclosure_copy_slug: str = Field(
        description=(
            "Referencia da versao de copy/disclosure (MVP: slug; mapa texto legal "
            "via processo tenant/CMS ou futura UI)."
        ),
    )
    updated_at: str | None = Field(
        default=None,
        description="Unset until a DB row exists (implicit defaults only).",
    )


class ContactPreferencesPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    marketing_opt_in: bool | None = None
    transactional_allowed: bool | None = None
    disclosure_copy_slug: str | None = Field(default=None, max_length=128)

    @field_validator("disclosure_copy_slug")
    @classmethod
    def slug_shape(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip()
        if len(s) < 1:
            raise ValueError("disclosure_copy_slug cannot be empty")
        return s[:128]


def _parse_contact_id(raw: str) -> str:
    cid = raw.strip()
    if not cid or len(cid) > 128 or _CONTACT_ID_PATTERN.match(cid) is None:
        raise HTTPException(status_code=422, detail="invalid contact id")
    return cid


def _defaults(cid: str) -> ContactPreferencesResponse:
    return ContactPreferencesResponse(
        contact_id=cid,
        marketing_opt_in=False,
        transactional_allowed=True,
        disclosure_copy_slug=_DEFAULT_COPY_SLUG,
        updated_at=None,
    )


@router.get(
    "/me/contacts/{contact_id}/preferences",
    response_model=ContactPreferencesResponse,
    responses=_RESP,
    summary="Preferencias LGPD/disclosure por contacto",
)
async def get_contact_preferences(
    contact_id: str,
    ctx: Annotated[TenantUserContext, Depends(console_tenant_user_context)],
) -> ContactPreferencesResponse:
    settings = get_settings()
    if not settings.database_url:
        raise HTTPException(status_code=503, detail="database unavailable")
    cid = _parse_contact_id(contact_id)
    async with tenant_session(ctx.tenant_id) as session:
        row = await session.scalar(
            select(TenantContactPreference).where(
                TenantContactPreference.tenant_id == ctx.tenant_id,
                TenantContactPreference.contact_id == cid,
            ),
        )
    if row is None:
        return _defaults(cid)
    return ContactPreferencesResponse(
        contact_id=cid,
        marketing_opt_in=row.marketing_opt_in,
        transactional_allowed=row.transactional_allowed,
        disclosure_copy_slug=row.disclosure_copy_slug,
        updated_at=row.updated_at.isoformat(),
    )


@router.patch(
    "/me/contacts/{contact_id}/preferences",
    response_model=ContactPreferencesResponse,
    responses=_RESP,
    summary="Atualizar preferencias por contacto (audit minimo)",
)
async def patch_contact_preferences(
    contact_id: str,
    body: ContactPreferencesPatch,
    ctx: Annotated[TenantUserContext, Depends(console_tenant_user_context)],
) -> ContactPreferencesResponse:
    settings = get_settings()
    if not settings.database_url:
        raise HTTPException(status_code=503, detail="database unavailable")
    if not (ctx.roles & CONTACT_PREFERENCE_WRITE_ROLES):
        raise HTTPException(status_code=403, detail="insufficient role")

    cid = _parse_contact_id(contact_id)
    patch = body.model_dump(exclude_unset=True)
    if not patch:
        raise HTTPException(status_code=422, detail="no fields to update")

    now = datetime.now(timezone.utc)
    changed_keys: list[str] = []

    async with tenant_session(ctx.tenant_id) as session:
        row = await session.scalar(
            select(TenantContactPreference).where(
                TenantContactPreference.tenant_id == ctx.tenant_id,
                TenantContactPreference.contact_id == cid,
            ),
        )

        if row is None:
            row = TenantContactPreference(
                tenant_id=ctx.tenant_id,
                contact_id=cid,
                marketing_opt_in=patch.get("marketing_opt_in", False),
                transactional_allowed=patch.get("transactional_allowed", True),
                disclosure_copy_slug=patch.get(
                    "disclosure_copy_slug",
                    _DEFAULT_COPY_SLUG,
                ),
                updated_at=now,
            )
            session.add(row)
            changed_keys = sorted(patch.keys())
        else:
            if "marketing_opt_in" in patch:
                nv = patch["marketing_opt_in"]
                assert nv is not None
                if nv != row.marketing_opt_in:
                    row.marketing_opt_in = nv
                    changed_keys.append("marketing_opt_in")
            if "transactional_allowed" in patch:
                nv = patch["transactional_allowed"]
                assert nv is not None
                if nv != row.transactional_allowed:
                    row.transactional_allowed = nv
                    changed_keys.append("transactional_allowed")
            if "disclosure_copy_slug" in patch:
                nv = patch["disclosure_copy_slug"]
                assert nv is not None
                if nv != row.disclosure_copy_slug:
                    row.disclosure_copy_slug = nv
                    changed_keys.append("disclosure_copy_slug")
            if changed_keys:
                row.updated_at = now

        if changed_keys:
            session.add(
                AuditEvent(
                    id=uuid.uuid4(),
                    tenant_id=ctx.tenant_id,
                    actor_user_id=ctx.actor_user_id,
                    resource_type="contact_preferences",
                    summary=f"patch:{cid}:{','.join(sorted(changed_keys))}",
                ),
            )

        await session.flush()
        await session.refresh(row)

    return ContactPreferencesResponse(
        contact_id=cid,
        marketing_opt_in=row.marketing_opt_in,
        transactional_allowed=row.transactional_allowed,
        disclosure_copy_slug=row.disclosure_copy_slug,
        updated_at=row.updated_at.isoformat(),
    )

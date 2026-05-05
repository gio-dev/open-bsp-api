"""Preferencias LGPD/disclosure por contacto (Story 6.3)."""

from __future__ import annotations

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
from app.whatsapp.meta_send import normalize_whatsapp_to

router = APIRouter(tags=["contacts"])

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
    marketing_consent_recorded_at: str | None = Field(
        default=None,
        description=(
            "Ultima vez em que marketing_opt_in passou a True (registo DSAR minimo). "
            "Nao e limpo em opt-out."
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
    s = raw.strip()
    if not s:
        raise HTTPException(status_code=422, detail="invalid contact id")
    try:
        return normalize_whatsapp_to(s if s.startswith("+") else f"+{s}")
    except ValueError:
        raise HTTPException(status_code=422, detail="invalid contact id")


def _defaults(cid: str) -> ContactPreferencesResponse:
    return ContactPreferencesResponse(
        contact_id=cid,
        marketing_opt_in=False,
        transactional_allowed=True,
        disclosure_copy_slug=_DEFAULT_COPY_SLUG,
        marketing_consent_recorded_at=None,
        updated_at=None,
    )


def _b(v: bool) -> str:
    return "true" if v else "false"


def _audit_prefs_summary(
    *,
    create: bool,
    cid: str,
    old_m: bool,
    old_t: bool,
    old_s: str,
    new_m: bool,
    new_t: bool,
    new_s: str,
) -> str:
    parts: list[str] = ["create" if create else "patch"]
    if new_m != old_m:
        parts.append(f"m:{_b(old_m)}->{_b(new_m)}")
    if new_t != old_t:
        parts.append(f"t:{_b(old_t)}->{_b(new_t)}")
    if new_s != old_s:
        parts.append(f"slug:{old_s[:40]}->{new_s[:40]}")
    body = "|".join(parts)
    return f"{cid}:{body[:950]}"


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
        marketing_consent_recorded_at=(
            row.marketing_consent_recorded_at.isoformat()
            if row.marketing_consent_recorded_at
            else None
        ),
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

    fs = body.model_fields_set
    if "marketing_opt_in" in fs and body.marketing_opt_in is None:
        raise HTTPException(status_code=422, detail="marketing_opt_in cannot be null")
    if "transactional_allowed" in fs and body.transactional_allowed is None:
        raise HTTPException(
            status_code=422, detail="transactional_allowed cannot be null"
        )
    if "disclosure_copy_slug" in fs and body.disclosure_copy_slug is None:
        raise HTTPException(
            status_code=422, detail="disclosure_copy_slug cannot be null"
        )

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

        is_create = row is None
        if row is None:
            old_m, old_t, old_s = False, True, _DEFAULT_COPY_SLUG
            new_m = bool(patch.get("marketing_opt_in", False))
            new_t = bool(patch.get("transactional_allowed", True))
            new_s = str(
                patch.get("disclosure_copy_slug", _DEFAULT_COPY_SLUG)
                or _DEFAULT_COPY_SLUG
            )
            row = TenantContactPreference(
                tenant_id=ctx.tenant_id,
                contact_id=cid,
                marketing_opt_in=new_m,
                transactional_allowed=new_t,
                disclosure_copy_slug=new_s,
                marketing_consent_recorded_at=now if new_m else None,
                updated_at=now,
            )
            session.add(row)
            changed_keys = sorted(patch.keys())
        else:
            old_m, old_t, old_s = (
                row.marketing_opt_in,
                row.transactional_allowed,
                row.disclosure_copy_slug,
            )
            if "marketing_opt_in" in patch:
                nv = patch["marketing_opt_in"]
                if nv != row.marketing_opt_in:
                    row.marketing_opt_in = nv
                    changed_keys.append("marketing_opt_in")
            if "transactional_allowed" in patch:
                nv = patch["transactional_allowed"]
                if nv != row.transactional_allowed:
                    row.transactional_allowed = nv
                    changed_keys.append("transactional_allowed")
            if "disclosure_copy_slug" in patch:
                nv = patch["disclosure_copy_slug"]
                if nv != row.disclosure_copy_slug:
                    row.disclosure_copy_slug = nv
                    changed_keys.append("disclosure_copy_slug")
            if changed_keys:
                row.updated_at = now
            fm = row.marketing_opt_in
            if fm and not old_m:
                row.marketing_consent_recorded_at = now

        new_m = row.marketing_opt_in
        new_t = row.transactional_allowed
        new_s = row.disclosure_copy_slug

        if changed_keys:
            summary = _audit_prefs_summary(
                create=is_create,
                cid=cid,
                old_m=old_m,
                old_t=old_t,
                old_s=old_s,
                new_m=new_m,
                new_t=new_t,
                new_s=new_s,
            )
            session.add(
                AuditEvent(
                    id=uuid.uuid4(),
                    tenant_id=ctx.tenant_id,
                    actor_user_id=ctx.actor_user_id,
                    resource_type="contact_preferences",
                    summary=summary,
                ),
            )

        await session.flush()
        await session.refresh(row)

    return ContactPreferencesResponse(
        contact_id=cid,
        marketing_opt_in=row.marketing_opt_in,
        transactional_allowed=row.transactional_allowed,
        disclosure_copy_slug=row.disclosure_copy_slug,
        marketing_consent_recorded_at=(
            row.marketing_consent_recorded_at.isoformat()
            if row.marketing_consent_recorded_at
            else None
        ),
        updated_at=row.updated_at.isoformat(),
    )

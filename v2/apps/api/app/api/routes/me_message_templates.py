"""Message templates WhatsApp + sinais de canal (Story 3.3)."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import delete, select

from app.core.config import get_settings
from app.core.errors import CanonicalErrorResponse
from app.db.models_message_templates import (
    WhatsappChannelSnapshot,
    WhatsappMessageTemplate,
)
from app.db.models_waba import WabaPhoneNumber
from app.db.session import tenant_session
from app.tenancy.deps import TenantUserContext, console_tenant_user_context
from app.tenancy.rbac import ORG_WRITE_ROLES
from app.whatsapp.templates_meta import (
    fetch_channel_signals,
    fetch_message_templates,
    map_template_record,
)

router = APIRouter(tags=["message-templates"])
log = logging.getLogger(__name__)

_ENV = frozenset({"development", "staging", "production", "sandbox"})

_TPL_RESPONSES = {
    401: {"model": CanonicalErrorResponse},
    403: {"model": CanonicalErrorResponse},
    409: {"model": CanonicalErrorResponse},
    422: {"model": CanonicalErrorResponse},
    503: {"model": CanonicalErrorResponse},
}


class MessageTemplateItem(BaseModel):
    id: str
    name: str
    language: str
    category: str | None = None
    display_status: str
    meta_status: str
    status_detail: str | None = None
    quality_score: str | None = None
    synced_at: str | None = None


class ChannelSignalsView(BaseModel):
    quality_rating: str | None = None
    messaging_limit_tier: str | None = None
    source: str = Field(
        description="stub | graph | unavailable | not_synced",
    )
    volume_incidents_crossref: bool = Field(
        default=False,
        description=(
            "True quando houver cruzamento com incidentes/volume (piloto: false)."
        ),
    )
    notes: str | None = None


class MessageTemplateListResponse(BaseModel):
    waba_id: str | None = None
    environment: str
    items: list[MessageTemplateItem]
    last_sync_at: str | None = None
    channel_signals: ChannelSignalsView


def _pick_waba_row(rows: list[WabaPhoneNumber]) -> WabaPhoneNumber | None:
    if not rows:
        return None
    for r in rows:
        if r.status == "active":
            return r
    return rows[0]


@router.get(
    "/me/message-templates",
    response_model=MessageTemplateListResponse,
    responses=_TPL_RESPONSES,
    summary="Message templates WhatsApp (cache Graph, primeira pagina no piloto)",
    description=(
        "Listagem com cache por tenant/WABA/ambiente. "
        "`refresh=true` (org_admin) sincroniza com a Graph API "
        "(sem paginacao neste piloto). "
        "Varias linhas no mesmo ambiente exigem query suficiente "
        "(tipicamente `phone_number_id`)."
    ),
)
async def list_message_templates(
    ctx: Annotated[TenantUserContext, Depends(console_tenant_user_context)],
    environment: str = Query(default="production", max_length=32),
    waba_id: str | None = Query(
        default=None,
        max_length=128,
        description="WABA id quando ha varios numeros no ambiente.",
    ),
    phone_number_id: str | None = Query(
        default=None,
        max_length=128,
        description="Phone number id (Meta) para desambiguar remetente.",
    ),
    refresh: bool = Query(
        default=False,
        description="Sincronizar com Meta (exige org_admin).",
    ),
) -> MessageTemplateListResponse:
    env = environment.strip()
    if env not in _ENV:
        raise HTTPException(
            status_code=422,
            detail=("environment must be development, staging, production, or sandbox"),
        )

    settings = get_settings()
    if not settings.database_url:
        raise HTTPException(status_code=503, detail="database unavailable")

    if refresh and not (ctx.roles & ORG_WRITE_ROLES):
        raise HTTPException(
            status_code=403,
            detail="org_admin role required to refresh templates from Meta",
        )

    if refresh and (
        not settings.whatsapp_cloud_api_stub
        and not settings.whatsapp_cloud_access_token
    ):
        raise HTTPException(
            status_code=503,
            detail="Meta credentials not configured for template sync",
        )

    wid = (waba_id or "").strip() or None
    pid = (phone_number_id or "").strip() or None

    async with tenant_session(ctx.tenant_id) as session:
        filters = [
            WabaPhoneNumber.tenant_id == ctx.tenant_id,
            WabaPhoneNumber.environment == env,
        ]
        if wid:
            filters.append(WabaPhoneNumber.waba_id == wid)
        if pid:
            filters.append(WabaPhoneNumber.phone_number_id == pid)

        r = await session.execute(select(WabaPhoneNumber).where(*filters))
        candidates = list(r.scalars().all())

        if len(candidates) > 1:
            raise HTTPException(
                status_code=409,
                detail=(
                    "multiple whatsapp numbers match this query; narrow with "
                    "phone_number_id (required when the same WABA has several lines)"
                ),
            )

        wpn = _pick_waba_row(candidates)

        if wpn is None:
            return MessageTemplateListResponse(
                waba_id=None,
                environment=env,
                items=[],
                last_sync_at=None,
                channel_signals=ChannelSignalsView(
                    source="unavailable",
                    notes="Sem numero WABA registado neste ambiente.",
                ),
            )

        now = datetime.now(timezone.utc)

        if refresh:
            async with httpx.AsyncClient(timeout=30.0) as hc:
                raw_tpls, tpl_ok = await fetch_message_templates(
                    settings, wpn.waba_id, client=hc
                )
                sig = await fetch_channel_signals(
                    settings, wpn.phone_number_id, client=hc
                )

            if tpl_ok:
                await session.execute(
                    delete(WhatsappMessageTemplate).where(
                        WhatsappMessageTemplate.tenant_id == ctx.tenant_id,
                        WhatsappMessageTemplate.waba_id == wpn.waba_id,
                        WhatsappMessageTemplate.environment == env,
                    )
                )
                for raw in raw_tpls:
                    disp, meta_st, detail, qual = map_template_record(raw)
                    mid = raw.get("id")
                    session.add(
                        WhatsappMessageTemplate(
                            id=uuid.uuid4(),
                            tenant_id=ctx.tenant_id,
                            waba_id=wpn.waba_id,
                            environment=env,
                            meta_template_id=str(mid)[:128] if mid else None,
                            name=str(raw.get("name") or "unknown")[:512],
                            language=str(raw.get("language") or "und")[:32],
                            category=(
                                str(raw["category"])[:64]
                                if raw.get("category")
                                else None
                            ),
                            display_status=disp,
                            meta_status=meta_st[:64],
                            status_detail=detail,
                            quality_score=qual,
                            synced_at=now,
                        )
                    )

                src = str(sig.get("source") or "unavailable")
                sig_notes: str | None = None
                if src == "unavailable":
                    sig_notes = "Graph nao devolveu sinais de canal (token ou erro)."
                qr_raw = sig.get("quality_rating")
                qt_raw = sig.get("messaging_limit_tier")
                qr = str(qr_raw)[:32] if qr_raw else None
                qt = str(qt_raw)[:64] if qt_raw else None

                snap = await session.scalar(
                    select(WhatsappChannelSnapshot).where(
                        WhatsappChannelSnapshot.tenant_id == ctx.tenant_id,
                        WhatsappChannelSnapshot.waba_id == wpn.waba_id,
                        WhatsappChannelSnapshot.environment == env,
                    )
                )
                if snap is None:
                    session.add(
                        WhatsappChannelSnapshot(
                            tenant_id=ctx.tenant_id,
                            waba_id=wpn.waba_id,
                            environment=env,
                            quality_rating=qr,
                            messaging_limit_tier=qt,
                            signal_source=src[:32],
                            notes=sig_notes[:512] if sig_notes else None,
                        )
                    )
                else:
                    snap.quality_rating = qr
                    snap.messaging_limit_tier = qt
                    snap.signal_source = src[:32]
                    snap.notes = sig_notes[:512] if sig_notes else None
                    snap.updated_at = now
                    session.add(snap)

                await session.flush()
            else:
                log.warning(
                    "template_refresh_skipped_fetch_failed",
                    extra={"tenant_id": str(ctx.tenant_id), "waba_id": wpn.waba_id},
                )

        res_tpl = await session.execute(
            select(WhatsappMessageTemplate)
            .where(
                WhatsappMessageTemplate.tenant_id == ctx.tenant_id,
                WhatsappMessageTemplate.waba_id == wpn.waba_id,
                WhatsappMessageTemplate.environment == env,
            )
            .order_by(
                WhatsappMessageTemplate.name.asc(),
                WhatsappMessageTemplate.language.asc(),
            )
        )
        tpl_rows = list(res_tpl.scalars().all())

        snap2 = await session.scalar(
            select(WhatsappChannelSnapshot).where(
                WhatsappChannelSnapshot.tenant_id == ctx.tenant_id,
                WhatsappChannelSnapshot.waba_id == wpn.waba_id,
                WhatsappChannelSnapshot.environment == env,
            )
        )

        last_sync: datetime | None = None
        for t in tpl_rows:
            if t.synced_at and (last_sync is None or t.synced_at > last_sync):
                last_sync = t.synced_at

    items = [
        MessageTemplateItem(
            id=str(t.id),
            name=t.name,
            language=t.language,
            category=t.category,
            display_status=t.display_status,
            meta_status=t.meta_status,
            status_detail=t.status_detail,
            quality_score=t.quality_score,
            synced_at=t.synced_at.isoformat() if t.synced_at else None,
        )
        for t in tpl_rows
    ]

    if snap2 is not None:
        cs = ChannelSignalsView(
            quality_rating=snap2.quality_rating,
            messaging_limit_tier=snap2.messaging_limit_tier,
            source=snap2.signal_source,
            notes=snap2.notes,
        )
    else:
        cs = ChannelSignalsView(
            source="not_synced",
            notes=(
                "Sinais de canal e cache de templates nao sincronizados; "
                "org_admin pode usar ?refresh=true."
            ),
        )

    return MessageTemplateListResponse(
        waba_id=wpn.waba_id,
        environment=env,
        items=items,
        last_sync_at=last_sync.isoformat() if last_sync else None,
        channel_signals=cs,
    )

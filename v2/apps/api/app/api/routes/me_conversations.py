"""Inbox: lista de conversas e mensagens (Story 4.1)."""

from __future__ import annotations

import base64
from datetime import datetime, timezone
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import and_, func, or_, select

from app.api.routes.me_inbox_tags import TagBrief, tags_for_conversation_ids
from app.core.config import get_settings
from app.core.errors import CanonicalErrorResponse
from app.db.models import TenantSettingsStub
from app.db.models_inbox import InboxConversation
from app.db.models_waba import WabaPhoneNumber
from app.db.models_webhook_inbound import WebhookInboundEvent
from app.db.session import tenant_session
from app.tenancy.deps import TenantUserContext, console_tenant_user_context

router = APIRouter(tags=["inbox"])

_ENV = frozenset({"development", "staging", "production", "sandbox"})

_CONV_LIST_RESPONSES = {
    401: {"model": CanonicalErrorResponse},
    403: {"model": CanonicalErrorResponse},
    409: {"model": CanonicalErrorResponse},
    422: {"model": CanonicalErrorResponse},
    503: {"model": CanonicalErrorResponse},
}

_CONV_THREAD_RESPONSES = {
    401: {"model": CanonicalErrorResponse},
    403: {"model": CanonicalErrorResponse},
    404: {"model": CanonicalErrorResponse},
    409: {"model": CanonicalErrorResponse},
    422: {"model": CanonicalErrorResponse},
    503: {"model": CanonicalErrorResponse},
}


class InboxHeaderWaba(BaseModel):
    waba_id: str
    phone_number_id: str
    display_phone_number: str


class InboxListHeader(BaseModel):
    tenant_display_name: str
    environment: str
    waba: InboxHeaderWaba | None = Field(
        default=None,
        description="Contexto do numero ativo para o ambiente (quando existe).",
    )


class ConversationListItem(BaseModel):
    id: str
    title: str | None
    contact_wa_id: str
    waba_id: str
    last_message_at: str | None
    preview: str | None = None
    tags: list[TagBrief] = Field(default_factory=list)


class ConversationListResponse(BaseModel):
    header: InboxListHeader
    items: list[ConversationListItem]
    limit: int
    next_cursor: str | None = None


class ThreadMessageItem(BaseModel):
    id: str
    source_id: str
    direction: Literal["inbound"] = "inbound"
    message_type: str
    body: str | None = None
    received_at: str | None = None


class ConversationThreadResponse(BaseModel):
    conversation_id: str
    header: InboxListHeader
    items: list[ThreadMessageItem]
    tags: list[TagBrief] = Field(default_factory=list)


def _resolve_list_environment(
    query_env: str | None,
    header_console: str | None,
    header_x_environment: str | None,
) -> str:
    raw = (query_env or header_console or header_x_environment or "production").strip()
    if raw not in _ENV:
        raise HTTPException(
            status_code=422,
            detail=("environment must be development, staging, production, or sandbox"),
        )
    return raw


def _pick_waba_row(rows: list[WabaPhoneNumber]) -> WabaPhoneNumber | None:
    if not rows:
        return None
    for r in rows:
        if r.status == "active":
            return r
    return rows[0]


def _narrow_waba_rows(
    rows: list[WabaPhoneNumber],
    waba_id: str | None,
    phone_number_id: str | None,
) -> list[WabaPhoneNumber]:
    out = rows
    wid = (waba_id or "").strip() or None
    pid = (phone_number_id or "").strip() or None
    if wid:
        out = [r for r in out if r.waba_id == wid]
    if pid:
        out = [r for r in out if r.phone_number_id == pid]
    return out


def _inbox_header_waba_or_409(
    waba_rows: list[WabaPhoneNumber],
    waba_id: str | None,
    phone_number_id: str | None,
) -> InboxHeaderWaba | None:
    narrowed = _narrow_waba_rows(waba_rows, waba_id, phone_number_id)
    if len(narrowed) > 1:
        raise HTTPException(
            status_code=409,
            detail=(
                "multiple whatsapp numbers match this query; narrow with "
                "phone_number_id (required when the same WABA has several lines)"
            ),
        )
    wpn = _pick_waba_row(narrowed) if narrowed else None
    if wpn is None:
        return None
    return InboxHeaderWaba(
        waba_id=wpn.waba_id,
        phone_number_id=wpn.phone_number_id,
        display_phone_number=wpn.display_phone_number,
    )


def _encode_cursor(ts: datetime | None, cid: str) -> str:
    ts_iso = ts.isoformat() if ts else ""
    raw = f"{ts_iso}\n{cid}".encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _decode_cursor(raw: str) -> tuple[datetime | None, str]:
    pad = "=" * (-len(raw) % 4)
    b = base64.urlsafe_b64decode(raw + pad)
    parts = b.decode("utf-8").split("\n", 1)
    if len(parts) != 2:
        raise ValueError("bad cursor")
    ts_s, cid = parts
    if not ts_s:
        return None, cid
    dt = datetime.fromisoformat(ts_s.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt, cid


def _body_from_payload(payload: dict) -> tuple[str, str | None]:
    msg = payload.get("message")
    if not isinstance(msg, dict):
        return "unknown", None
    mtype = str(msg.get("type") or "unknown")
    body: str | None = None
    if mtype == "text":
        tx = msg.get("text")
        if isinstance(tx, dict):
            b = tx.get("body")
            if isinstance(b, str):
                body = b[:4096]
    return mtype, body


@router.get(
    "/me/conversations",
    response_model=ConversationListResponse,
    responses=_CONV_LIST_RESPONSES,
)
async def list_conversations(
    ctx: Annotated[TenantUserContext, Depends(console_tenant_user_context)],
    environment: str | None = Query(default=None, max_length=32),
    x_console_environment: str | None = Header(
        default=None,
        alias="X-Console-Environment",
    ),
    x_environment: str | None = Header(default=None, alias="X-Environment"),
    waba_id: str | None = Query(
        default=None,
        max_length=128,
        description="WABA id quando ha varios numeros no ambiente.",
    ),
    phone_number_id: str | None = Query(
        default=None,
        max_length=128,
        description="Phone number id (Meta) para desambiguar contexto de inbox.",
    ),
    limit: int = Query(default=50, ge=1, le=100),
    cursor: str | None = Query(default=None, max_length=512),
) -> ConversationListResponse:
    env = _resolve_list_environment(environment, x_console_environment, x_environment)
    settings = get_settings()
    if not settings.database_url:
        raise HTTPException(status_code=503, detail="database unavailable")

    cursor_ts: datetime | None = None
    cursor_id: str | None = None
    if cursor:
        try:
            cursor_ts, cid = _decode_cursor(cursor.strip())
            cursor_id = cid
        except (ValueError, UnicodeDecodeError) as e:
            raise HTTPException(status_code=422, detail="invalid cursor") from e

    async with tenant_session(ctx.tenant_id) as session:
        settings_row = await session.scalar(
            select(TenantSettingsStub).where(
                TenantSettingsStub.tenant_id == ctx.tenant_id
            )
        )
        display_name = (
            str(settings_row.display_name)
            if settings_row is not None
            else "Organization"
        )

        r_waba = await session.execute(
            select(WabaPhoneNumber).where(
                WabaPhoneNumber.tenant_id == ctx.tenant_id,
                WabaPhoneNumber.environment == env,
            )
        )
        waba_rows = list(r_waba.scalars().all())
        header_waba = _inbox_header_waba_or_409(
            waba_rows,
            (waba_id or "").strip() or None,
            (phone_number_id or "").strip() or None,
        )

        conds = [
            InboxConversation.tenant_id == ctx.tenant_id,
            InboxConversation.environment == env,
        ]
        if cursor_ts is not None and cursor_id is not None:
            conds.append(
                or_(
                    InboxConversation.last_activity_at < cursor_ts,
                    and_(
                        InboxConversation.last_activity_at == cursor_ts,
                        InboxConversation.id < cursor_id,
                    ),
                )
            )

        stmt = (
            select(InboxConversation)
            .where(*conds)
            .order_by(
                InboxConversation.last_activity_at.desc().nulls_last(),
                InboxConversation.id.desc(),
            )
            .limit(limit + 1)
        )
        rows = list((await session.execute(stmt)).scalars().all())

    next_cur: str | None = None
    if len(rows) > limit:
        rows = rows[:limit]
        last = rows[-1]
        next_cur = _encode_cursor(last.last_activity_at, last.id)

    conv_ids = [c.id for c in rows]
    tag_map: dict[str, list[TagBrief]] = {}
    if conv_ids:
        async with tenant_session(ctx.tenant_id) as session:
            tag_map = await tags_for_conversation_ids(session, ctx.tenant_id, conv_ids)

    items_out: list[ConversationListItem] = []
    for c in rows:
        items_out.append(
            ConversationListItem(
                id=c.id,
                title=c.title,
                contact_wa_id=c.contact_wa_id,
                waba_id=c.waba_id,
                last_message_at=(
                    c.last_activity_at.isoformat() if c.last_activity_at else None
                ),
                preview=None,
                tags=tag_map.get(c.id, []),
            )
        )

    return ConversationListResponse(
        header=InboxListHeader(
            tenant_display_name=display_name,
            environment=env,
            waba=header_waba,
        ),
        items=items_out,
        limit=limit,
        next_cursor=next_cur,
    )


@router.get(
    "/me/conversations/{conversation_id}/messages",
    response_model=ConversationThreadResponse,
    responses=_CONV_THREAD_RESPONSES,
)
async def list_conversation_messages(
    conversation_id: str,
    ctx: Annotated[TenantUserContext, Depends(console_tenant_user_context)],
    environment: str | None = Query(default=None, max_length=32),
    x_console_environment: str | None = Header(
        default=None,
        alias="X-Console-Environment",
    ),
    x_environment: str | None = Header(default=None, alias="X-Environment"),
    waba_id: str | None = Query(
        default=None,
        max_length=128,
        description="WABA id quando ha varios numeros no ambiente.",
    ),
    phone_number_id: str | None = Query(
        default=None,
        max_length=128,
        description="Phone number id (Meta) para desambiguar contexto de inbox.",
    ),
    limit: int = Query(default=200, ge=1, le=500),
) -> ConversationThreadResponse:
    env = _resolve_list_environment(environment, x_console_environment, x_environment)
    cid = conversation_id.strip()
    if not cid or len(cid) > 128:
        raise HTTPException(status_code=422, detail="invalid conversation id")

    settings = get_settings()
    if not settings.database_url:
        raise HTTPException(status_code=503, detail="database unavailable")

    async with tenant_session(ctx.tenant_id) as session:
        conv = await session.scalar(
            select(InboxConversation).where(
                InboxConversation.tenant_id == ctx.tenant_id,
                InboxConversation.id == cid,
                InboxConversation.environment == env,
            )
        )
        if conv is None:
            raise HTTPException(status_code=404, detail="conversation not found")

        settings_row = await session.scalar(
            select(TenantSettingsStub).where(
                TenantSettingsStub.tenant_id == ctx.tenant_id
            )
        )
        display_name = (
            str(settings_row.display_name)
            if settings_row is not None
            else "Organization"
        )
        r_waba = await session.execute(
            select(WabaPhoneNumber).where(
                WabaPhoneNumber.tenant_id == ctx.tenant_id,
                WabaPhoneNumber.environment == env,
            )
        )
        waba_rows = list(r_waba.scalars().all())
        header_waba = _inbox_header_waba_or_409(
            waba_rows,
            (waba_id or "").strip() or None,
            (phone_number_id or "").strip() or None,
        )

        from_expr = WebhookInboundEvent.payload["message"]["from"].astext
        norm_from = func.regexp_replace(from_expr, r"\D", "", "g")

        m_stmt = (
            select(WebhookInboundEvent)
            .where(
                WebhookInboundEvent.tenant_id == ctx.tenant_id,
                WebhookInboundEvent.event_kind == "message",
                WebhookInboundEvent.waba_id == conv.waba_id,
                norm_from == conv.contact_wa_id,
            )
            .order_by(
                WebhookInboundEvent.message_ts.asc().nulls_last(),
                WebhookInboundEvent.created_at.asc(),
            )
            .limit(limit)
        )
        events = list((await session.execute(m_stmt)).scalars().all())
        tmap = await tags_for_conversation_ids(session, ctx.tenant_id, [cid])
        thread_tags = tmap.get(cid, [])

    thread_items: list[ThreadMessageItem] = []
    for ev in events:
        payload = ev.payload if isinstance(ev.payload, dict) else {}
        mtype, body = _body_from_payload(payload)
        thread_items.append(
            ThreadMessageItem(
                id=str(ev.id),
                source_id=ev.source_id,
                direction="inbound",
                message_type=mtype,
                body=body,
                received_at=(
                    ev.message_ts.isoformat() if ev.message_ts is not None else None
                ),
            )
        )

    return ConversationThreadResponse(
        conversation_id=cid,
        header=InboxListHeader(
            tenant_display_name=display_name,
            environment=env,
            waba=header_waba,
        ),
        items=thread_items,
        tags=thread_tags,
    )

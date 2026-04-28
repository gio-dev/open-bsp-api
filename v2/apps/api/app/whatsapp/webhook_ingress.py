"""Enfileiramento de webhooks WhatsApp (tenant + idempotencia). Story 3.1."""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Literal, cast
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert

from app.core.config import Settings
from app.db.models_webhook_inbound import WebhookInboundEvent
from app.db.session import platform_session, tenant_session
from app.inbox.sync import upsert_inbox_conversation_from_inbound
from app.whatsapp.identity import resolve_inbound_identity

log = logging.getLogger(__name__)


def meta_unix_ts(raw: str | int | float | None) -> datetime | None:
    """Converte timestamp Meta (unix segundos, string ou numero) para UTC."""
    if raw is None:
        return None
    try:
        if isinstance(raw, str):
            sec = int(raw.strip())
        else:
            sec = int(raw)
    except (ValueError, TypeError):
        return None
    return datetime.fromtimestamp(sec, tz=timezone.utc)


def payload_has_queueable_items(payload: dict[str, Any]) -> bool:
    """True se existir entrada/alteracao com mensagens ou estados com id Meta."""
    for entry in payload.get("entry") or []:
        if not isinstance(entry, dict):
            continue
        waba_raw = entry.get("id")
        if not isinstance(waba_raw, str) or not waba_raw.strip():
            continue
        for change in entry.get("changes") or []:
            if not isinstance(change, dict):
                continue
            value = change.get("value")
            if not isinstance(value, dict):
                continue
            for msg in value.get("messages") or []:
                if isinstance(msg, dict) and isinstance(msg.get("id"), str):
                    mid = msg["id"].strip()
                    if mid:
                        return True
            for st in value.get("statuses") or []:
                if isinstance(st, dict) and isinstance(st.get("id"), str):
                    sid = st["id"].strip()
                    if sid:
                        return True
    return False


def ensure_fresh_event(
    event_at: datetime | None,
    *,
    max_age_seconds: int,
    request_id: str,
    waba_id: str,
    source_id: str,
) -> None:
    if max_age_seconds <= 0:
        return
    if event_at is None:
        log.warning(
            "webhook_event_missing_timestamp",
            extra={
                "request_id": request_id,
                "waba_id": waba_id,
                "source_id": source_id,
                "max_age_seconds": max_age_seconds,
            },
        )
        return
    now = datetime.now(timezone.utc)
    if now - event_at > timedelta(seconds=max_age_seconds):
        log.warning(
            "webhook_replay_rejected",
            extra={
                "request_id": request_id,
                "waba_id": waba_id,
                "source_id": source_id,
                "event_ts": event_at.isoformat(),
                "max_age_seconds": max_age_seconds,
            },
        )
        raise HTTPException(
            status_code=409,
            detail="webhook event outside acceptance window",
        )


ResolveStatus = Literal["ok", "none", "ambiguous"]


async def resolve_tenant_for_waba(
    waba_id: str, phone_number_id: str | None
) -> tuple[UUID | None, ResolveStatus]:
    async with platform_session() as session:
        pid = phone_number_id.strip() if phone_number_id else None
        row = await session.execute(
            text("SELECT tenant_id, resolve_status FROM resolve_waba_tenant(:w, :p)"),
            {"w": waba_id, "p": pid},
        )
        m = row.mappings().first()
        if not m:
            return None, "none"
        st = cast(str | None, m.get("resolve_status"))
        tid = cast(UUID | None, m.get("tenant_id"))
        if st == "ambiguous":
            return None, "ambiguous"
        if st == "ok" and tid is not None:
            return tid, "ok"
        return None, "none"


@dataclass(frozen=True)
class _EnqueueRow:
    tenant_id: UUID
    waba_id: str
    source_id: str
    event_kind: str
    payload: dict[str, Any]
    message_ts: datetime | None
    contact_wa_id: str | None = None
    phone_number_id: str | None = None


async def enqueue_whatsapp_payload(
    *,
    payload: dict[str, Any],
    settings: Settings,
    request_id: str,
) -> dict[str, int]:
    """Resolve tenant, anti-replay, insert idempotente por (waba_id, source_id)."""
    if not settings.database_url:
        if payload_has_queueable_items(payload):
            raise HTTPException(
                status_code=503,
                detail="database required to accept inbound webhook notifications",
            )
        return {"enqueued": 0, "deduplicated": 0, "skipped": 0}

    rows: list[_EnqueueRow] = []
    skipped = 0
    wh_max_age = settings.whatsapp_webhook_max_event_age_seconds

    for entry in payload.get("entry") or []:
        if not isinstance(entry, dict):
            continue
        waba_raw = entry.get("id")
        if not isinstance(waba_raw, str) or not waba_raw.strip():
            continue
        waba_id = waba_raw.strip()

        for change in entry.get("changes") or []:
            if not isinstance(change, dict):
                continue
            value = change.get("value")
            if not isinstance(value, dict):
                continue

            meta = value.get("metadata")
            phone_id: str | None = None
            if isinstance(meta, dict):
                pn = meta.get("phone_number_id")
                if isinstance(pn, str) and pn.strip():
                    phone_id = pn.strip()

            tenant_id, waba_resolve = await resolve_tenant_for_waba(waba_id, phone_id)
            if waba_resolve == "ambiguous":
                log.warning(
                    "webhook_waba_ambiguous",
                    extra={
                        "request_id": request_id,
                        "waba_id": waba_id,
                        "phone_number_id": phone_id,
                    },
                )
                raise HTTPException(
                    status_code=409,
                    detail="whatsapp business account tenant mapping is ambiguous",
                )
            if tenant_id is None:
                log.warning(
                    "webhook_unknown_waba",
                    extra={
                        "request_id": request_id,
                        "waba_id": waba_id,
                        "phone_number_id": phone_id,
                    },
                )
                raise HTTPException(
                    status_code=404,
                    detail="whatsapp business account not registered",
                )

            for msg in value.get("messages") or []:
                if not isinstance(msg, dict):
                    continue
                sid_raw = msg.get("id")
                if not isinstance(sid_raw, str) or not sid_raw.strip():
                    skipped += 1
                    continue
                source_id = sid_raw.strip()
                ts = meta_unix_ts(msg.get("timestamp"))
                if ts is None:
                    log.warning(
                        "webhook_event_missing_timestamp",
                        extra={
                            "request_id": request_id,
                            "waba_id": waba_id,
                            "source_id": source_id,
                            "max_age_seconds": wh_max_age,
                        },
                    )
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "webhook event timestamp required for acceptance window"
                        ),
                    )
                ensure_fresh_event(
                    ts,
                    max_age_seconds=wh_max_age,
                    request_id=request_id,
                    waba_id=waba_id,
                    source_id=source_id,
                )
                ident = resolve_inbound_identity(value, msg)
                raw_from = msg.get("from")
                contact_digits: str | None = None
                if isinstance(raw_from, str) and raw_from.strip():
                    contact_digits = (
                        "".join(ch for ch in raw_from.strip() if ch.isdigit()) or None
                    )
                rows.append(
                    _EnqueueRow(
                        tenant_id=tenant_id,
                        waba_id=waba_id,
                        source_id=source_id,
                        event_kind="message",
                        payload={
                            "waba_id": waba_id,
                            "change": change,
                            "message": msg,
                            "identity": (
                                {
                                    "bsuid": ident.bsuid,
                                    "wa_id": ident.wa_id,
                                }
                                if ident
                                else None
                            ),
                        },
                        message_ts=ts,
                        contact_wa_id=contact_digits,
                        phone_number_id=phone_id,
                    )
                )

            for st in value.get("statuses") or []:
                if not isinstance(st, dict):
                    continue
                sid_raw = st.get("id")
                if not isinstance(sid_raw, str) or not sid_raw.strip():
                    skipped += 1
                    continue
                source_id = sid_raw.strip()
                ts = meta_unix_ts(st.get("timestamp"))
                if ts is None:
                    log.warning(
                        "webhook_event_missing_timestamp",
                        extra={
                            "request_id": request_id,
                            "waba_id": waba_id,
                            "source_id": source_id,
                            "max_age_seconds": wh_max_age,
                        },
                    )
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "webhook event timestamp required for acceptance window"
                        ),
                    )
                ensure_fresh_event(
                    ts,
                    max_age_seconds=wh_max_age,
                    request_id=request_id,
                    waba_id=waba_id,
                    source_id=source_id,
                )
                rows.append(
                    _EnqueueRow(
                        tenant_id=tenant_id,
                        waba_id=waba_id,
                        source_id=source_id,
                        event_kind="status",
                        payload={"waba_id": waba_id, "change": change, "status": st},
                        message_ts=ts,
                    )
                )

    if not rows:
        return {"enqueued": 0, "deduplicated": 0, "skipped": skipped}

    by_tenant: dict[UUID, list[_EnqueueRow]] = defaultdict(list)
    for r in rows:
        by_tenant[r.tenant_id].append(r)

    enqueued = 0
    deduplicated = 0

    for tid, trows in by_tenant.items():
        async with tenant_session(tid) as session:
            for r in trows:
                stmt = (
                    insert(WebhookInboundEvent)
                    .values(
                        tenant_id=r.tenant_id,
                        waba_id=r.waba_id,
                        source_id=r.source_id,
                        event_kind=r.event_kind,
                        payload=r.payload,
                        message_ts=r.message_ts,
                    )
                    .on_conflict_do_nothing(
                        constraint="uq_webhook_inbound_waba_source",
                    )
                    .returning(WebhookInboundEvent.id)
                )
                res = await session.execute(stmt)
                if res.scalar_one_or_none() is not None:
                    enqueued += 1
                    if (
                        r.event_kind == "message"
                        and r.contact_wa_id
                        and r.message_ts is not None
                    ):
                        await upsert_inbox_conversation_from_inbound(
                            session,
                            tenant_id=tid,
                            waba_id=r.waba_id,
                            contact_wa_id=r.contact_wa_id,
                            phone_number_id=r.phone_number_id,
                            message_ts=r.message_ts,
                        )
                else:
                    deduplicated += 1

    return {
        "enqueued": enqueued,
        "deduplicated": deduplicated,
        "skipped": skipped,
    }

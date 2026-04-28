"""Processamento da fila de envio WhatsApp (Story 3.2)."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select

from app.core.config import get_settings
from app.db.models_outbound import OutboundWhatsappMessage
from app.db.models_waba import WabaPhoneNumber
from app.db.session import tenant_session
from app.whatsapp.meta_send import send_whatsapp_text

log = logging.getLogger(__name__)


async def deliver_outbound_message(message_id: UUID, tenant_id: UUID) -> None:
    """Uma passagem: Meta API + estado (`sent` = aceite Graph, nao lido no device)."""
    settings = get_settings()
    async with tenant_session(tenant_id) as session:
        stmt = (
            select(OutboundWhatsappMessage)
            .where(OutboundWhatsappMessage.id == message_id)
            .with_for_update()
        )
        row = (await session.execute(stmt)).scalar_one_or_none()
        if row is None:
            return
        if row.status not in ("queued", "rate_limited"):
            return
        now = datetime.now(timezone.utc)
        if row.next_attempt_at is not None and row.next_attempt_at > now:
            return

        waba = await session.get(WabaPhoneNumber, row.waba_phone_id)
        if waba is None:
            row.status = "failed"
            row.upstream_fault = "platform"
            row.error_code = "missing_waba_phone"
            row.error_message = "sender phone configuration removed"
            return

        if row.message_type != "text":
            row.status = "failed"
            row.upstream_fault = "platform"
            row.error_code = "unsupported_type"
            row.error_message = row.message_type
            return

        text_body = ""
        if isinstance(row.payload, dict):
            t = row.payload.get("text")
            if isinstance(t, dict):
                tb = t.get("body")
                if isinstance(tb, str):
                    text_body = tb

        row.status = "sending"
        await session.flush()

        try:
            result = await send_whatsapp_text(
                phone_number_id=waba.phone_number_id,
                to_digits=row.to_recipient,
                body=text_body,
                settings=settings,
            )
        except Exception as exc:  # noqa: BLE001 - falha de rede/httpx; estado terminal
            log.exception(
                "outbound_meta_send_exception",
                extra={"message_id": str(message_id), "tenant_id": str(tenant_id)},
            )
            row.attempt_count = int(row.attempt_count or 0) + 1
            row.status = "failed"
            row.upstream_fault = "platform"
            row.error_code = "send_exception"
            row.error_message = str(exc)[:1024]
            row.next_attempt_at = None
            return

        row.attempt_count = int(row.attempt_count or 0) + 1

        if result.ok:
            row.status = "sent"
            row.meta_message_id = result.meta_message_id
            row.upstream_fault = None
            row.error_code = None
            row.error_message = None
            row.next_attempt_at = None
        elif result.http_status == 429 or result.error_code == "rate_limited":
            row.status = "rate_limited"
            row.upstream_fault = "meta"
            row.error_code = result.error_code
            row.error_message = result.error_message
            sec = result.retry_after_seconds or 60
            row.next_attempt_at = now + timedelta(seconds=sec)
            log.warning(
                "outbound_scheduled_retry",
                extra={
                    "message_id": str(message_id),
                    "retry_after_seconds": sec,
                },
            )
        elif result.error_code == "missing_token":
            row.status = "failed"
            row.upstream_fault = "platform"
            row.error_code = result.error_code
            row.error_message = result.error_message
        else:
            row.status = "failed"
            row.upstream_fault = "meta"
            row.error_code = result.error_code
            row.error_message = result.error_message

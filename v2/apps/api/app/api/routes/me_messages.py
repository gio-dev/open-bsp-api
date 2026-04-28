"""Envio de mensagens WhatsApp (saida) ? Story 3.2."""

from __future__ import annotations

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.core.errors import CanonicalErrorResponse
from app.db.models_outbound import OutboundWhatsappMessage
from app.db.models_waba import WabaPhoneNumber
from app.db.session import tenant_session
from app.tenancy.deps import TenantUserContext, console_message_send_context
from app.whatsapp.meta_send import normalize_whatsapp_to
from app.whatsapp.outbound_worker import deliver_outbound_message

router = APIRouter(tags=["messages"])

_ENVIRONMENTS = frozenset(
    {"development", "staging", "production", "sandbox"},
)

_MSG_RESPONSES = {
    401: {"model": CanonicalErrorResponse},
    403: {"model": CanonicalErrorResponse},
    404: {"model": CanonicalErrorResponse},
    409: {"model": CanonicalErrorResponse},
    422: {"model": CanonicalErrorResponse},
    503: {"model": CanonicalErrorResponse},
}


class TextSubPayload(BaseModel):
    body: str = Field(max_length=4096)


class SendWhatsAppMessageBody(BaseModel):
    to: str = Field(max_length=32)
    type: Literal["text"] = "text"
    text: TextSubPayload
    environment: str = Field(default="production", max_length=32)
    phone_number_id: str | None = Field(default=None, max_length=128)

    @field_validator("environment")
    @classmethod
    def environment_ok(cls, v: str) -> str:
        if v not in _ENVIRONMENTS:
            raise ValueError(
                "environment must be development, staging, production, or sandbox"
            )
        return v


class MessageSendAccepted(BaseModel):
    """Ack imediato: fila; worker + sweep reprocessam; 429 persiste Retry-After."""

    id: str = Field(description="ID interno do envio.")
    status: str = Field(
        description=(
            "Estado persistido: tipicamente `queued` ate o worker concluir; "
            "`sent` apos resposta Graph (nao implica entregue no dispositivo)."
        ),
    )
    upstream_fault: str | None = Field(
        default=None, description="Se falhou: meta ou platform."
    )


async def _resolve_sender_waba(
    session,
    tenant_id: UUID,
    environment: str,
    phone_number_id: str | None,
) -> WabaPhoneNumber:
    filters = [
        WabaPhoneNumber.tenant_id == tenant_id,
        WabaPhoneNumber.environment == environment,
        WabaPhoneNumber.status == "active",
    ]
    if phone_number_id:
        filters.append(WabaPhoneNumber.phone_number_id == phone_number_id)
    cnt_stmt = select(func.count()).select_from(WabaPhoneNumber).where(*filters)
    n = (await session.execute(cnt_stmt)).scalar_one()
    if n == 0:
        raise HTTPException(
            status_code=404,
            detail="no active whatsapp sender for this environment",
        )
    if n > 1 and not phone_number_id:
        raise HTTPException(
            status_code=409,
            detail=(
                "multiple whatsapp senders for this environment; "
                "specify phone_number_id"
            ),
        )
    q = (
        select(WabaPhoneNumber)
        .where(*filters)
        .order_by(WabaPhoneNumber.created_at)
        .limit(1)
    )
    res = await session.execute(q)
    w = res.scalar_one()
    return w


@router.post(
    "/me/messages/send",
    status_code=202,
    response_model=MessageSendAccepted,
    responses=_MSG_RESPONSES,
    summary="Enviar mensagem WhatsApp (fila + worker)",
)
async def send_whatsapp_message(
    background_tasks: BackgroundTasks,
    body: SendWhatsAppMessageBody,
    ctx: Annotated[TenantUserContext, Depends(console_message_send_context)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> MessageSendAccepted:
    settings = get_settings()
    if not settings.database_url:
        raise HTTPException(status_code=503, detail="database unavailable")

    try:
        to_digits = normalize_whatsapp_to(body.to)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    idem = (idempotency_key or "").strip() or None
    if idem and len(idem) > 128:
        raise HTTPException(status_code=422, detail="Idempotency-Key too long")

    async with tenant_session(ctx.tenant_id) as session:
        if idem:
            r0 = await session.execute(
                select(OutboundWhatsappMessage).where(
                    OutboundWhatsappMessage.tenant_id == ctx.tenant_id,
                    OutboundWhatsappMessage.idempotency_key == idem,
                )
            )
            existing = r0.scalar_one_or_none()
            if existing is not None:
                return MessageSendAccepted(
                    id=str(existing.id),
                    status=existing.status,
                    upstream_fault=existing.upstream_fault,
                )

        waba = await _resolve_sender_waba(
            session, ctx.tenant_id, body.environment, body.phone_number_id
        )

        row = OutboundWhatsappMessage(
            tenant_id=ctx.tenant_id,
            waba_phone_id=waba.id,
            to_recipient=to_digits,
            message_type=body.type,
            payload={"text": {"body": body.text.body}},
            status="queued",
            idempotency_key=idem,
        )
        session.add(row)
        try:
            await session.flush()
        except IntegrityError:
            await session.rollback()
            async with tenant_session(ctx.tenant_id) as session2:
                r1 = await session2.execute(
                    select(OutboundWhatsappMessage).where(
                        OutboundWhatsappMessage.tenant_id == ctx.tenant_id,
                        OutboundWhatsappMessage.idempotency_key == idem,
                    )
                )
                hit = r1.scalar_one_or_none()
                if hit is None:
                    raise HTTPException(
                        status_code=409,
                        detail="idempotent send conflict",
                    ) from None
                return MessageSendAccepted(
                    id=str(hit.id),
                    status=hit.status,
                    upstream_fault=hit.upstream_fault,
                )

        mid = row.id

    background_tasks.add_task(deliver_outbound_message, mid, ctx.tenant_id)

    return MessageSendAccepted(id=str(mid), status="queued", upstream_fault=None)

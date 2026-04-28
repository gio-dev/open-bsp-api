"""Upsert inbox_conversations a partir de mensagens webhook (Story 4.1)."""

from __future__ import annotations

import hashlib
from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models_inbox import InboxConversation
from app.db.models_waba import WabaPhoneNumber


def derived_conversation_id(tenant_id: UUID, waba_id: str, contact_wa_id: str) -> str:
    """Id estavel por tenant + WABA + contacto (novas conversas)."""
    h = hashlib.sha256(
        f"{tenant_id}:{waba_id}:{contact_wa_id}".encode(),
    ).hexdigest()[:18]
    return f"c-{h}"


async def upsert_inbox_conversation_from_inbound(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    waba_id: str,
    contact_wa_id: str,
    phone_number_id: str | None,
    message_ts: datetime,
) -> None:
    wpn_id: UUID | None = None
    environment = "production"
    if phone_number_id:
        wpn = await session.scalar(
            select(WabaPhoneNumber).where(
                WabaPhoneNumber.tenant_id == tenant_id,
                WabaPhoneNumber.phone_number_id == phone_number_id,
            )
        )
        if wpn is not None:
            wpn_id = wpn.id
            environment = wpn.environment
    conv_id = derived_conversation_id(tenant_id, waba_id, contact_wa_id)
    ins = pg_insert(InboxConversation).values(
        id=conv_id,
        tenant_id=tenant_id,
        waba_id=waba_id,
        contact_wa_id=contact_wa_id,
        environment=environment,
        waba_phone_number_id=wpn_id,
        last_activity_at=message_ts,
    )
    stmt = ins.on_conflict_do_update(
        constraint="uq_inbox_conv_tenant_waba_contact",
        set_={
            "last_activity_at": func.greatest(
                func.coalesce(
                    InboxConversation.last_activity_at,
                    ins.excluded.last_activity_at,
                ),
                ins.excluded.last_activity_at,
            ),
            "updated_at": func.now(),
            "environment": ins.excluded.environment,
            "waba_phone_number_id": func.coalesce(
                ins.excluded.waba_phone_number_id,
                InboxConversation.waba_phone_number_id,
            ),
        },
    )
    await session.execute(stmt)

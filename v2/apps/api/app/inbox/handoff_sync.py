"""Contrato interno: motor (Epic 5.5) persiste handoff (Story 4.3)."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.db.models_inbox import InboxConversationHandoff

_VALID = frozenset(
    {
        "automated",
        "pending_handoff",
        "queued",
        "accepted",
        "failed",
    }
)


async def upsert_handoff_from_engine(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    conversation_id: str,
    handoff_state: str,
    intent_summary: str | None = None,
    bot_last_output: str | None = None,
    queue_id: str | None = None,
) -> None:
    """Idempotente por `conversation_id`. Nao altera `claimed_by_user_id`."""
    if handoff_state not in _VALID:
        raise ValueError(f"invalid handoff_state: {handoff_state}")

    ins = pg_insert(InboxConversationHandoff).values(
        conversation_id=conversation_id,
        tenant_id=tenant_id,
        intent_summary=intent_summary,
        bot_last_output=bot_last_output,
        handoff_state=handoff_state,
        queue_id=queue_id,
    )
    stmt = ins.on_conflict_do_update(
        index_elements=[InboxConversationHandoff.conversation_id],
        set_={
            "intent_summary": ins.excluded.intent_summary,
            "bot_last_output": ins.excluded.bot_last_output,
            "handoff_state": ins.excluded.handoff_state,
            "queue_id": ins.excluded.queue_id,
            "tenant_id": ins.excluded.tenant_id,
            "updated_at": func.now(),
        },
    )
    await session.execute(stmt)

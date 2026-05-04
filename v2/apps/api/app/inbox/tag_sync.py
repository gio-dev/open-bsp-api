"""Etiquetas na conversa a partir do motor (Story 5.5)."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models_inbox import InboxConversationTag, InboxTag


async def append_conversation_tag_by_name(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    conversation_id: str,
    tag_name: str,
) -> None:
    """Idempotente: adiciona etiqueta por nome (obtem-ou-cria)."""
    name = tag_name.strip()
    if not name:
        raise ValueError("tag_name required")

    tag = await session.scalar(
        select(InboxTag).where(
            InboxTag.tenant_id == tenant_id,
            InboxTag.name == name,
        ),
    )
    if tag is None:
        tag = InboxTag(tenant_id=tenant_id, name=name)
        session.add(tag)
        await session.flush()

    ins = (
        pg_insert(InboxConversationTag)
        .values(
            conversation_id=conversation_id,
            tag_id=tag.id,
            tenant_id=tenant_id,
        )
        .on_conflict_do_nothing(
            index_elements=["conversation_id", "tag_id"],
        )
    )
    await session.execute(ins)

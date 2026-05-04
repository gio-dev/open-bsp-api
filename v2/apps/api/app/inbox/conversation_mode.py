"""Modo bot/humano por conversa (Story 6.2), derivado do estado de handoff.

Semantica de `since` (exposta em ISO 8601 no GET `/mode`):

- `human_active`: carimbo `updated_at` da linha de handoff quando presente; caso
  contrario `updated_at` da conversa (fallback defensivo).
- `bot_active`: ultimo `updated_at` da linha de handoff se existir, senao
  `last_activity_at` da conversa, senao `updated_at` da conversa; ultimo fallback
  `created_at`.

Isto e um **instante de referencia** para UI ("desde quando este modo e coerente
com o ultimo evento persistido"), nao necessariamente o primeiro momento em que
o modo comecou nem um evento de auditoria completo.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from app.db.models_inbox import InboxConversation, InboxConversationHandoff

_VALID_HANDOFF = frozenset(
    {
        "automated",
        "pending_handoff",
        "queued",
        "accepted",
        "failed",
    },
)

_HUMAN_PIPELINE = frozenset({"pending_handoff", "queued", "accepted", "failed"})

ConversationModeLiteral = Literal["bot_active", "human_active"]


def conversation_mode_and_since(
    *,
    conv: InboxConversation,
    handoff: InboxConversationHandoff | None,
) -> tuple[ConversationModeLiteral, datetime]:
    st = (
        handoff.handoff_state
        if handoff is not None and handoff.handoff_state in _VALID_HANDOFF
        else "automated"
    )
    if st in _HUMAN_PIPELINE:
        mode: ConversationModeLiteral = "human_active"
        since = handoff.updated_at if handoff is not None else conv.updated_at
    else:
        mode = "bot_active"
        since = (
            (handoff.updated_at if handoff is not None else None)
            or conv.last_activity_at
            or conv.updated_at
        )
    since = since or conv.created_at
    return mode, since

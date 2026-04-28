"""Handoff por conversa (Story 4.3): leitura e PATCH operador/supervisao.

Epic 5.5 (motor de regras) deve persistir linhas em `inbox_conversation_handoffs` via
`app.inbox.handoff_sync.upsert_handoff_from_engine` (ou SQL directo) na mesma unidade de
trabalho que processa o evento; estas rotas sao apenas para consola.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select

from app.core.config import get_settings
from app.core.errors import CanonicalErrorResponse
from app.db.models_inbox import InboxConversation, InboxConversationHandoff
from app.db.session import tenant_session
from app.tenancy.deps import TenantUserContext, console_tenant_user_context
from app.tenancy.rbac import INBOX_TAG_ROLES, ORG_WRITE_ROLES

router = APIRouter(tags=["inbox"])

_ENV = frozenset({"development", "staging", "production", "sandbox"})

_VALID_STATES = frozenset(
    {
        "automated",
        "pending_handoff",
        "queued",
        "accepted",
        "failed",
    }
)

_ACCEPT_ELIGIBLE_STATES = frozenset(
    {
        "pending_handoff",
        "queued",
        "failed",
    }
)

_HANDOFF_GET_RESPONSES = {
    401: {"model": CanonicalErrorResponse},
    403: {"model": CanonicalErrorResponse},
    404: {"model": CanonicalErrorResponse},
    422: {"model": CanonicalErrorResponse},
    503: {"model": CanonicalErrorResponse},
}

_HANDOFF_PATCH_RESPONSES = {
    401: {"model": CanonicalErrorResponse},
    403: {"model": CanonicalErrorResponse},
    404: {"model": CanonicalErrorResponse},
    409: {"model": CanonicalErrorResponse},
    422: {"model": CanonicalErrorResponse},
    503: {"model": CanonicalErrorResponse},
}


class HandoffResponse(BaseModel):
    conversation_id: str
    intent_summary: str | None = None
    bot_last_output: str | None = None
    handoff_state: Literal[
        "automated",
        "pending_handoff",
        "queued",
        "accepted",
        "failed",
    ]
    queue_id: str | None = None
    claimed_by_user_id: str | None = None
    updated_at: str | None = None


class HandoffPatchBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accept: bool | None = None
    queue_id: str | None = Field(default=None, max_length=128)


def _resolve_env(
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


def _row_to_response(cid: str, row: InboxConversationHandoff | None) -> HandoffResponse:
    if row is None:
        return HandoffResponse(
            conversation_id=cid,
            intent_summary=None,
            bot_last_output=None,
            handoff_state="automated",
            queue_id=None,
            claimed_by_user_id=None,
            updated_at=None,
        )
    st = row.handoff_state
    if st not in _VALID_STATES:
        st = "automated"
    return HandoffResponse(
        conversation_id=cid,
        intent_summary=row.intent_summary,
        bot_last_output=row.bot_last_output,
        handoff_state=st,  # type: ignore[arg-type]
        queue_id=row.queue_id,
        claimed_by_user_id=(
            str(row.claimed_by_user_id) if row.claimed_by_user_id else None
        ),
        updated_at=row.updated_at.isoformat() if row.updated_at else None,
    )


@router.get(
    "/me/conversations/{conversation_id}/handoff",
    response_model=HandoffResponse,
    responses=_HANDOFF_GET_RESPONSES,
    summary="Contexto de handoff da conversa",
)
async def get_conversation_handoff(
    conversation_id: str,
    ctx: Annotated[TenantUserContext, Depends(console_tenant_user_context)],
    environment: str | None = Query(default=None, max_length=32),
    x_console_environment: str | None = Header(
        default=None,
        alias="X-Console-Environment",
    ),
    x_environment: str | None = Header(default=None, alias="X-Environment"),
) -> HandoffResponse:
    env = _resolve_env(environment, x_console_environment, x_environment)
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

        row = await session.scalar(
            select(InboxConversationHandoff).where(
                InboxConversationHandoff.tenant_id == ctx.tenant_id,
                InboxConversationHandoff.conversation_id == cid,
            )
        )

    return _row_to_response(cid, row)


@router.patch(
    "/me/conversations/{conversation_id}/handoff",
    response_model=HandoffResponse,
    responses=_HANDOFF_PATCH_RESPONSES,
    summary="Atualizar fila (supervisao) ou assumir handoff (operador)",
    description=(
        "`accept: true` exige linha de handoff existente e estado em "
        "`pending_handoff`, `queued` ou `failed` (ou ja aceite pelo mesmo "
        "operador, idempotente). Estado `automated` devolve 422."
    ),
)
async def patch_conversation_handoff(
    conversation_id: str,
    body: HandoffPatchBody,
    ctx: Annotated[TenantUserContext, Depends(console_tenant_user_context)],
    environment: str | None = Query(default=None, max_length=32),
    x_console_environment: str | None = Header(
        default=None,
        alias="X-Console-Environment",
    ),
    x_environment: str | None = Header(default=None, alias="X-Environment"),
) -> HandoffResponse:
    env = _resolve_env(environment, x_console_environment, x_environment)
    cid = conversation_id.strip()
    if not cid or len(cid) > 128:
        raise HTTPException(status_code=422, detail="invalid conversation id")

    patch = body.model_dump(exclude_unset=True)
    if not patch:
        raise HTTPException(status_code=422, detail="no fields to update")

    if "queue_id" in patch and not (ctx.roles & ORG_WRITE_ROLES):
        raise HTTPException(
            status_code=403,
            detail="org_admin role required to change routing queue",
        )

    if patch.get("accept") is True and not (ctx.roles & INBOX_TAG_ROLES):
        raise HTTPException(
            status_code=403,
            detail="inbox role required to accept handoff",
        )

    if patch.get("accept") is True and ctx.actor_user_id is None:
        raise HTTPException(
            status_code=422,
            detail="user identity required to accept handoff",
        )

    settings = get_settings()
    if not settings.database_url:
        raise HTTPException(status_code=503, detail="database unavailable")

    now = datetime.now(timezone.utc)

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

        accept = patch.get("accept") is True

        if accept:
            assert ctx.actor_user_id is not None
            row = await session.scalar(
                select(InboxConversationHandoff)
                .where(
                    InboxConversationHandoff.tenant_id == ctx.tenant_id,
                    InboxConversationHandoff.conversation_id == cid,
                )
                .with_for_update()
            )
            if row is None:
                raise HTTPException(
                    status_code=422,
                    detail="no handoff record exists for this conversation",
                )
            st = row.handoff_state
            if st == "accepted":
                if row.claimed_by_user_id is None:
                    raise HTTPException(
                        status_code=422,
                        detail="invalid handoff state for accept",
                    )
                if row.claimed_by_user_id != ctx.actor_user_id:
                    raise HTTPException(
                        status_code=409,
                        detail="handoff already accepted by another operator",
                    )
            elif st not in _ACCEPT_ELIGIBLE_STATES:
                raise HTTPException(
                    status_code=422,
                    detail="cannot accept handoff in current state",
                )
            else:
                row.handoff_state = "accepted"
                row.claimed_by_user_id = ctx.actor_user_id
                row.updated_at = now

            if "queue_id" in patch:
                row.queue_id = patch["queue_id"]
                row.updated_at = now
        else:
            row = await session.scalar(
                select(InboxConversationHandoff).where(
                    InboxConversationHandoff.tenant_id == ctx.tenant_id,
                    InboxConversationHandoff.conversation_id == cid,
                )
            )
            if row is None:
                row = InboxConversationHandoff(
                    conversation_id=cid,
                    tenant_id=ctx.tenant_id,
                    handoff_state="automated",
                )
                session.add(row)
                await session.flush()

            if "queue_id" in patch:
                row.queue_id = patch["queue_id"]
                row.updated_at = now

        await session.flush()
        await session.refresh(row)

    return _row_to_response(cid, row)

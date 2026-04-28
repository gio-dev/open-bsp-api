"""Etiquetas de inbox / conversas (Story 4.2)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import delete, select

from app.core.config import get_settings
from app.core.errors import CanonicalErrorResponse
from app.db.models_inbox import InboxConversation, InboxConversationTag, InboxTag
from app.db.session import tenant_session
from app.tenancy.deps import TenantUserContext, console_inbox_tag_context

router = APIRouter(tags=["inbox"])

_MAX_TAGS_PER_CONVERSATION = 20

_INBOX_TAG_RESPONSES = {
    401: {"model": CanonicalErrorResponse},
    403: {"model": CanonicalErrorResponse},
    422: {"model": CanonicalErrorResponse},
    503: {"model": CanonicalErrorResponse},
}

_PATCH_TAG_RESPONSES = {
    401: {"model": CanonicalErrorResponse},
    403: {"model": CanonicalErrorResponse},
    404: {"model": CanonicalErrorResponse},
    422: {"model": CanonicalErrorResponse},
    503: {"model": CanonicalErrorResponse},
}

_ENV = frozenset({"development", "staging", "production", "sandbox"})


class TagBrief(BaseModel):
    id: str = Field(description="UUID da etiqueta no tenant.")
    name: str


class InboxTagsListResponse(BaseModel):
    items: list[TagBrief]


class CreateInboxTagBody(BaseModel):
    name: str = Field(min_length=1, max_length=128)


class CreateInboxTagResponse(TagBrief):
    pass


class PatchConversationTagsBody(BaseModel):
    tag_ids: list[UUID] = Field(
        default_factory=list,
        max_length=_MAX_TAGS_PER_CONVERSATION,
        description=(
            f"Conjunto completo de etiquetas da conversa (max "
            f"{_MAX_TAGS_PER_CONVERSATION})."
        ),
    )


class PatchConversationTagsResponse(BaseModel):
    conversation_id: str
    tags: list[TagBrief]


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


def _normalize_tag_name(raw: str) -> str:
    name = raw.strip()
    if not name:
        raise HTTPException(status_code=422, detail="tag name required")
    if len(name) > 128:
        raise HTTPException(status_code=422, detail="tag name too long")
    return name


async def tags_for_conversation_ids(
    session,
    tenant_id: UUID,
    conversation_ids: list[str],
) -> dict[str, list[TagBrief]]:
    if not conversation_ids:
        return {}
    stmt = (
        select(
            InboxConversationTag.conversation_id,
            InboxTag.id,
            InboxTag.name,
        )
        .join(InboxTag, InboxTag.id == InboxConversationTag.tag_id)
        .where(
            InboxConversationTag.tenant_id == tenant_id,
            InboxConversationTag.conversation_id.in_(conversation_ids),
        )
        .order_by(InboxTag.name.asc())
    )
    rows = (await session.execute(stmt)).all()
    out: dict[str, list[TagBrief]] = {cid: [] for cid in conversation_ids}
    for cid, tid, name in rows:
        b = TagBrief(id=str(tid), name=str(name))
        if cid in out:
            out[cid].append(b)
    return out


@router.get(
    "/me/inbox/tags",
    response_model=InboxTagsListResponse,
    responses=_INBOX_TAG_RESPONSES,
)
async def list_inbox_tags(
    ctx: Annotated[TenantUserContext, Depends(console_inbox_tag_context)],
) -> InboxTagsListResponse:
    settings = get_settings()
    if not settings.database_url:
        raise HTTPException(status_code=503, detail="database unavailable")

    async with tenant_session(ctx.tenant_id) as session:
        stmt = (
            select(InboxTag)
            .where(InboxTag.tenant_id == ctx.tenant_id)
            .order_by(InboxTag.name.asc())
        )
        tags = list((await session.execute(stmt)).scalars().all())
    return InboxTagsListResponse(
        items=[TagBrief(id=str(t.id), name=t.name) for t in tags],
    )


@router.post(
    "/me/inbox/tags",
    response_model=CreateInboxTagResponse,
    responses=_INBOX_TAG_RESPONSES,
    summary="Criar etiqueta de inbox (idempotente por nome)",
    description=(
        "Cria uma etiqueta partilhada no tenant. Se ja existir etiqueta com o mesmo "
        "nome (apos normalizacao trim), devolve **200** com o **id** existente ? "
        "equivalente a obter-or-criar, util para duplo clique ou corridas leves."
    ),
)
async def create_inbox_tag(
    body: CreateInboxTagBody,
    ctx: Annotated[TenantUserContext, Depends(console_inbox_tag_context)],
) -> CreateInboxTagResponse:
    settings = get_settings()
    if not settings.database_url:
        raise HTTPException(status_code=503, detail="database unavailable")

    name = _normalize_tag_name(body.name)
    tid_out: str
    name_out: str
    async with tenant_session(ctx.tenant_id) as session:
        existing = await session.scalar(
            select(InboxTag).where(
                InboxTag.tenant_id == ctx.tenant_id,
                InboxTag.name == name,
            )
        )
        if existing is not None:
            tid_out, name_out = str(existing.id), existing.name
        else:
            tag = InboxTag(tenant_id=ctx.tenant_id, name=name)
            session.add(tag)
            await session.flush()
            tid_out, name_out = str(tag.id), tag.name

    return CreateInboxTagResponse(id=tid_out, name=name_out)


@router.patch(
    "/me/conversations/{conversation_id}/tags",
    response_model=PatchConversationTagsResponse,
    responses=_PATCH_TAG_RESPONSES,
)
async def patch_conversation_tags(
    conversation_id: str,
    body: PatchConversationTagsBody,
    ctx: Annotated[TenantUserContext, Depends(console_inbox_tag_context)],
    environment: str | None = Query(default=None, max_length=32),
    x_console_environment: str | None = Header(
        default=None,
        alias="X-Console-Environment",
    ),
    x_environment: str | None = Header(default=None, alias="X-Environment"),
) -> PatchConversationTagsResponse:
    env = _resolve_env(environment, x_console_environment, x_environment)
    cid = conversation_id.strip()
    if not cid or len(cid) > 128:
        raise HTTPException(status_code=422, detail="invalid conversation id")

    tag_ids = list(dict.fromkeys(body.tag_ids))
    if len(tag_ids) > _MAX_TAGS_PER_CONVERSATION:
        raise HTTPException(
            status_code=422,
            detail=f"at most {_MAX_TAGS_PER_CONVERSATION} tags per conversation",
        )

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

        if tag_ids:
            r = await session.execute(
                select(InboxTag.id).where(
                    InboxTag.tenant_id == ctx.tenant_id,
                    InboxTag.id.in_(tag_ids),
                )
            )
            found = {row[0] for row in r.all()}
            missing = [x for x in tag_ids if x not in found]
            if missing:
                raise HTTPException(
                    status_code=422,
                    detail="one or more tag_ids are unknown for this tenant",
                )

        await session.execute(
            delete(InboxConversationTag).where(
                InboxConversationTag.tenant_id == ctx.tenant_id,
                InboxConversationTag.conversation_id == cid,
            )
        )
        for tid in tag_ids:
            session.add(
                InboxConversationTag(
                    conversation_id=cid,
                    tag_id=tid,
                    tenant_id=ctx.tenant_id,
                )
            )
        await session.flush()
        tmap = await tags_for_conversation_ids(session, ctx.tenant_id, [cid])

    return PatchConversationTagsResponse(
        conversation_id=cid,
        tags=tmap.get(cid, []),
    )

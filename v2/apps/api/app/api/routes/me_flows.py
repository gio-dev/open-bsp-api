"""Rotas fluxos /me: rascunhos (5.1), sandbox (5.2), publish (5.3).

POST validate, CRUD drafts, publish, sandbox-run (query environment=sandbox).
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import and_, func, select
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.errors import (
    CanonicalErrorResponse,
    CanonicalValidationErrorResponse,
    canonical_error_body,
    canonical_validation_error_body,
)
from app.db.models import AuditEvent
from app.db.models_flows import (
    TenantFlowDraft,
    TenantFlowPublishActivation,
    TenantFlowPublishVersion,
    TenantFlowSandboxRun,
)
from app.db.session import tenant_session
from app.services.flow_sandbox import simulate_sandbox_run
from app.services.flow_validation import validate_flow_definition
from app.tenancy.deps import (
    TenantUserContext,
    console_flow_editor_context,
    console_tenant_user_context,
)
from app.tenancy.rbac import roles_may_publish_flow

logger = logging.getLogger(__name__)

_DB_UNAVAILABLE = "servico de dados temporariamente indisponivel"


def _sandbox_atdd_flow_key_allowed(settings: Settings) -> bool:
    """Literal atdd-flow e artefacto CI/dev; desligado em consola real por omissao."""
    return settings.auth_dev_stub or settings.allow_atdd_sandbox_flow_key


_RESPONSES_VALIDATE = {
    200: {},
    401: {"model": CanonicalErrorResponse},
    403: {"model": CanonicalErrorResponse},
    422: {"model": CanonicalValidationErrorResponse},
}
_RESPONSES_RW = {
    401: {"model": CanonicalErrorResponse},
    403: {"model": CanonicalErrorResponse},
    404: {"model": CanonicalErrorResponse},
    422: {"model": CanonicalValidationErrorResponse},
    503: {"model": CanonicalErrorResponse},
}

ATDD_SANDBOX_FLOW_KEY = "atdd-flow"
_ATDD_SANDBOX_STUB: dict[str, Any] = {
    "nodes": [
        {"id": "t_atdd", "kind": "trigger"},
        {"id": "a_atdd", "kind": "action"},
    ],
    "edges": [{"source": "t_atdd", "target": "a_atdd"}],
}

router = APIRouter(tags=["flows"])


class FlowValidationIssue(BaseModel):
    field: str
    message: str


class FlowValidateResponse(BaseModel):
    valid: bool
    errors: list[FlowValidationIssue] = Field(default_factory=list)


class FlowDraftCreateBody(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Meu fluxo",
                    "definition": {
                        "nodes": [
                            {"id": "t1", "kind": "trigger"},
                            {"id": "a1", "kind": "action"},
                        ],
                        "edges": [{"source": "t1", "target": "a1"}],
                    },
                }
            ],
        },
    )

    name: str = Field(..., min_length=1, max_length=256)
    definition: dict[str, Any] | None = None


class FlowDraftPatchBody(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=256)
    definition: dict[str, Any] | None = None


class FlowDraftSummaryOut(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    valid: bool
    updated_at: datetime


class FlowDraftListResponse(BaseModel):
    items: list[FlowDraftSummaryOut]


class FlowDraftDetailOut(FlowDraftSummaryOut):
    definition: dict[str, Any]


class SandboxRunBody(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"fixture_message": {"type": "text", "body": "hi"}},
                {
                    "fixture_message": {
                        "type": "text",
                        "body": "ola",
                        "contact": {"wa_id": "+stub", "profile_name": "Cliente stub"},
                    },
                },
            ],
        },
    )

    fixture_message: dict[str, Any] = Field(default_factory=dict)


class SandboxRunResponse(BaseModel):
    """Resultado deterministico sandbox; mesmo `run_id` em persistencia opcional."""

    run_id: uuid.UUID = Field(
        description=(
            "Identificador do run. Se `persisted` e false, pode nao existir linha "
            "em `tenant_flow_sandbox_runs` (falha transitoria de BD); usar "
            "`correlation_id` e trace para suporte."
        ),
    )
    status: Literal["succeeded", "failed"]
    environment: Literal["sandbox"] = "sandbox"
    trace: list[str]
    correlation_id: str
    persisted: bool = Field(
        description=(
            "True se o run foi persistido em tenant_flow_sandbox_runs; False sem "
            "DATABASE_URL ou apos falha de escrita (trace ainda valido para debug)."
        ),
    )
    fixture_fingerprint: str = Field(
        description="Primeiros 16 hex do SHA-256 do fixture_message (JSON canonico).",
    )


PublishEnvironment = Literal["development", "staging", "production"]


class FlowPublishBody(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"environment": "staging"}]},
    )

    environment: PublishEnvironment = Field(
        ...,
        description="Ambiente runtime alvo (nao inclui sandbox).",
    )


class FlowPublishResponse(BaseModel):
    activation_id: uuid.UUID
    environment: PublishEnvironment
    flow_draft_id: uuid.UUID | None = None
    flow_external_key: str | None = None
    activated_at: datetime
    idempotent_repeat: bool = Field(
        description=(
            "True quando o snapshot ja era o versao activa neste ambiente "
            "(POST idempotente)."
        ),
    )


class FlowVersionItemOut(BaseModel):
    version_id: uuid.UUID
    environment: PublishEnvironment
    definition_fingerprint: str
    definition_fingerprint_prefix: str = Field(max_length=16)
    published_at: datetime
    published_by_user_id: uuid.UUID | None = None
    publish_activation_id: uuid.UUID | None = None
    flow_draft_id: uuid.UUID | None = None
    flow_external_key: str | None = None

    @classmethod
    def from_row(cls, row: TenantFlowPublishVersion) -> FlowVersionItemOut:
        fp = row.definition_fingerprint
        pre = fp[:16] if len(fp) >= 16 else fp
        return cls(
            version_id=row.id,
            environment=row.environment,
            definition_fingerprint=fp,
            definition_fingerprint_prefix=pre,
            published_at=row.published_at,
            published_by_user_id=row.published_by_user_id,
            publish_activation_id=row.publish_activation_id,
            flow_draft_id=row.flow_draft_id,
            flow_external_key=row.flow_external_key,
        )


class FlowVersionListResponse(BaseModel):
    items: list[FlowVersionItemOut]
    limit: int
    offset: int
    total: int


class FlowVersionDetailOut(FlowVersionItemOut):
    definition: dict[str, Any] = Field(
        description="Snapshot JSON imutavel na publicacao (materialidade)."
    )

    @classmethod
    def from_row(cls, row: TenantFlowPublishVersion) -> FlowVersionDetailOut:
        base = FlowVersionItemOut.from_row(row)
        return cls(**base.model_dump(), definition=dict(row.definition_snapshot or {}))


_RESPONSES_PUBLISH = {
    200: {"model": FlowPublishResponse},
    401: {"model": CanonicalErrorResponse},
    403: {"model": CanonicalErrorResponse},
    404: {"model": CanonicalErrorResponse},
    409: {"model": CanonicalErrorResponse},
    422: {"model": CanonicalValidationErrorResponse},
    503: {"model": CanonicalErrorResponse},
}


_RESPONSES_SANDBOX = {
    200: {"model": SandboxRunResponse},
    401: {"model": CanonicalErrorResponse},
    403: {"model": CanonicalErrorResponse},
    404: {"model": CanonicalErrorResponse},
    422: {"model": CanonicalValidationErrorResponse},
    503: {"model": CanonicalErrorResponse},
}

_RESPONSES_VERSION_LIST = {
    200: {"model": FlowVersionListResponse},
    401: {"model": CanonicalErrorResponse},
    404: {"model": CanonicalErrorResponse},
    422: {"model": CanonicalValidationErrorResponse},
    503: {"model": CanonicalErrorResponse},
}

_RESPONSES_VERSION_DETAIL = {
    200: {"model": FlowVersionDetailOut},
    401: {"model": CanonicalErrorResponse},
    404: {"model": CanonicalErrorResponse},
    422: {"model": CanonicalValidationErrorResponse},
    503: {"model": CanonicalErrorResponse},
}


def _now() -> datetime:
    return datetime.now(UTC)


def _fixture_message_json_bytes(fixture: dict[str, Any]) -> int:
    return len(
        json.dumps(fixture, sort_keys=True, default=str).encode("utf-8"),
    )


_EMPTY_DEF: dict[str, Any] = {"nodes": [], "edges": []}


def _definition_fingerprint_sha256(definition: dict[str, Any]) -> str:
    """SHA-256 hex (64 chars) do grafo serializado; JSON canonico.

    Evolucoes de schema do grafo: nao alterar este algoritmo sem migracao acordada
    (idempotencia e linhas `definition_fingerprint` existentes dependem dele).
    """
    return hashlib.sha256(
        json.dumps(definition, sort_keys=True, default=str).encode("utf-8"),
    ).hexdigest()


def _summarize(row: TenantFlowDraft) -> FlowDraftSummaryOut:
    errs = validate_flow_definition(dict(row.definition or {}))
    return FlowDraftSummaryOut(
        id=row.id,
        tenant_id=row.tenant_id,
        name=row.name,
        valid=len(errs) == 0,
        updated_at=row.updated_at,
    )


def _detail(row: TenantFlowDraft) -> FlowDraftDetailOut:
    base = _summarize(row)
    defin = dict(row.definition or _EMPTY_DEF)
    return FlowDraftDetailOut(**base.model_dump(), definition=defin)


def _must_db(settings: Settings) -> None:
    if not settings.database_url:
        raise HTTPException(
            status_code=503,
            detail=_DB_UNAVAILABLE,
        )


def _flow_validation_json_response(
    req: Request,
    errs: list[dict[str, str]],
) -> JSONResponse:
    rid = getattr(req.state, "request_id", str(uuid.uuid4()))
    return JSONResponse(
        status_code=422,
        headers={"x-request-id": rid},
        content=canonical_validation_error_body(
            message="flow validation failed",
            request_id=rid,
            errors=list(errs),
        ),
    )


def _raise_db_unavailable(exc: OperationalError) -> None:
    logger.warning("flows database operational error", exc_info=exc)
    raise HTTPException(status_code=503, detail=_DB_UNAVAILABLE) from exc


@router.post(
    "/me/flows/validate",
    response_model=FlowValidateResponse,
    responses=_RESPONSES_VALIDATE,
)
async def post_validate_flow(
    req: Request,
    ctx: Annotated[TenantUserContext, Depends(console_flow_editor_context)],
    body: dict[str, Any] = Body(
        ...,
        openapi_examples={
            "valid_minimal": {
                "summary": "Fluxo minimo valido (200)",
                "value": {
                    "nodes": [
                        {"id": "t1", "kind": "trigger"},
                        {"id": "a1", "kind": "action"},
                    ],
                    "edges": [{"source": "t1", "target": "a1"}],
                },
            },
            "invalid_empty": {
                "summary": "Grafo vazio (422 errors[])",
                "value": {"nodes": [], "edges": []},
            },
        },
    ),
) -> FlowValidateResponse | JSONResponse:
    """Valida grafico sem persistir (`console_flow_editor_context`: tenant + RBAC)."""
    _ = ctx.tenant_id

    errs = validate_flow_definition(body)
    if errs:
        return _flow_validation_json_response(req, errs)
    return FlowValidateResponse(valid=True, errors=[])


@router.get(
    "/me/flows",
    response_model=FlowDraftListResponse,
    responses=_RESPONSES_RW,
)
async def list_flow_drafts(
    ctx: Annotated[TenantUserContext, Depends(console_flow_editor_context)],
) -> FlowDraftListResponse:
    settings = get_settings()
    _must_db(settings)
    async with tenant_session(ctx.tenant_id) as session:
        try:
            res = await session.execute(
                select(TenantFlowDraft)
                .order_by(TenantFlowDraft.updated_at.desc())
                .limit(100),
            )
        except OperationalError as e:
            _raise_db_unavailable(e)
        rows = res.scalars().all()
        return FlowDraftListResponse(items=[_summarize(r) for r in rows])


@router.post(
    "/me/flows",
    response_model=FlowDraftDetailOut,
    responses=_RESPONSES_RW,
    status_code=201,
)
async def create_flow_draft(
    req: Request,
    ctx: Annotated[TenantUserContext, Depends(console_flow_editor_context)],
    body: FlowDraftCreateBody,
) -> FlowDraftDetailOut | JSONResponse:
    settings = get_settings()
    _must_db(settings)

    defin = dict(body.definition if body.definition is not None else _EMPTY_DEF)
    val_errs = validate_flow_definition(defin)
    if val_errs:
        return _flow_validation_json_response(req, val_errs)
    fid = uuid.uuid4()
    now = _now()
    async with tenant_session(ctx.tenant_id) as session:
        try:
            row = TenantFlowDraft(
                id=fid,
                tenant_id=ctx.tenant_id,
                name=body.name,
                definition=defin,
                created_at=now,
                updated_at=now,
            )
            session.add(row)
            await session.flush()
        except OperationalError as e:
            _raise_db_unavailable(e)
    return _detail(row)


async def _get_draft(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    fid: uuid.UUID,
) -> TenantFlowDraft | None:
    res = await session.execute(
        select(TenantFlowDraft).where(
            TenantFlowDraft.tenant_id == tenant_id,
            TenantFlowDraft.id == fid,
        ),
    )
    return res.scalar_one_or_none()


async def _get_flow_publish_activation(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    environment: str,
    *,
    draft_id: uuid.UUID | None,
    external_key: str | None,
    for_update: bool = False,
) -> TenantFlowPublishActivation | None:
    if draft_id is not None:
        stmt = select(TenantFlowPublishActivation).where(
            TenantFlowPublishActivation.tenant_id == tenant_id,
            TenantFlowPublishActivation.environment == environment,
            TenantFlowPublishActivation.flow_draft_id == draft_id,
        )
        if for_update:
            stmt = stmt.with_for_update()
        res = await session.execute(stmt)
        return res.scalar_one_or_none()
    if external_key is not None:
        stmt = select(TenantFlowPublishActivation).where(
            TenantFlowPublishActivation.tenant_id == tenant_id,
            TenantFlowPublishActivation.environment == environment,
            TenantFlowPublishActivation.flow_external_key == external_key,
        )
        if for_update:
            stmt = stmt.with_for_update()
        res = await session.execute(stmt)
        return res.scalar_one_or_none()
    return None


async def _flow_versions_identity_or_err(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    flow_id: str,
    req: Request,
    settings: Settings,
) -> tuple[uuid.UUID | None, str | None] | JSONResponse:
    """Mesma identidade de fluxo que `POST .../publish` (UUID de draft ou stub)."""
    stripped = flow_id.strip()
    if stripped == ATDD_SANDBOX_FLOW_KEY:
        if not _sandbox_atdd_flow_key_allowed(settings):
            return _flow_validation_json_response(
                req,
                [
                    {
                        "field": "flow_id",
                        "message": (
                            "chave atdd-flow so com AUTH_DEV_STUB ou "
                            "ALLOW_ATDD_SANDBOX_FLOW_KEY=true"
                        ),
                    },
                ],
            )
        return (None, ATDD_SANDBOX_FLOW_KEY)
    try:
        uuid_fid = uuid.UUID(stripped)
    except ValueError:
        return _flow_validation_json_response(
            req,
            [
                {
                    "field": "flow_id",
                    "message": (
                        "use o UUID do rascunho; chave atdd-flow apenas dev/CI "
                        "(stub ou ALLOW_ATDD_SANDBOX_FLOW_KEY)"
                    ),
                },
            ],
        )
    row = await _get_draft(session, tenant_id, uuid_fid)
    if row is None:
        rid = getattr(req.state, "request_id", str(uuid.uuid4()))
        return JSONResponse(
            status_code=404,
            headers={"x-request-id": rid},
            content=canonical_error_body(
                code="http_404",
                message="draft not found",
                request_id=rid,
            ),
        )
    return (uuid_fid, None)


@router.get(
    "/me/flows/{flow_id}/versions/{version_id}",
    response_model=FlowVersionDetailOut,
    responses=_RESPONSES_VERSION_DETAIL,
)
async def get_flow_publish_version_detail(
    req: Request,
    flow_id: Annotated[str, Path(min_length=1, max_length=256)],
    version_id: uuid.UUID,
    ctx: Annotated[TenantUserContext, Depends(console_tenant_user_context)],
) -> FlowVersionDetailOut | JSONResponse:
    """Snapshot material de uma publicacao (lista resumida em `.../versions`)."""
    settings = get_settings()
    _must_db(settings)
    async with tenant_session(ctx.tenant_id) as session:
        try:
            ident = await _flow_versions_identity_or_err(
                session, ctx.tenant_id, flow_id, req, settings
            )
            if isinstance(ident, JSONResponse):
                return ident
            draft_pk, ext_key = ident
            stmt = select(TenantFlowPublishVersion).where(
                TenantFlowPublishVersion.tenant_id == ctx.tenant_id,
                TenantFlowPublishVersion.id == version_id,
            )
            if draft_pk is not None:
                stmt = stmt.where(TenantFlowPublishVersion.flow_draft_id == draft_pk)
            else:
                stmt = stmt.where(
                    TenantFlowPublishVersion.flow_external_key == ext_key,
                )
            res = await session.execute(stmt)
            row = res.scalar_one_or_none()
        except OperationalError as e:
            _raise_db_unavailable(e)
    if row is None:
        raise HTTPException(status_code=404, detail="version not found")
    return FlowVersionDetailOut.from_row(row)


@router.get(
    "/me/flows/{flow_id}/versions",
    response_model=FlowVersionListResponse,
    responses=_RESPONSES_VERSION_LIST,
)
async def list_flow_publish_versions(
    req: Request,
    flow_id: Annotated[str, Path(min_length=1, max_length=256)],
    ctx: Annotated[TenantUserContext, Depends(console_tenant_user_context)],
    environment: Annotated[
        PublishEnvironment | None,
        Query(description="Filtrar por ambiente runtime (opcional)."),
    ] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> FlowVersionListResponse | JSONResponse:
    """Historico append-only ordenado por `published_at` mais recentes primeiro."""
    settings = get_settings()
    _must_db(settings)
    async with tenant_session(ctx.tenant_id) as session:
        try:
            ident = await _flow_versions_identity_or_err(
                session, ctx.tenant_id, flow_id, req, settings
            )
            if isinstance(ident, JSONResponse):
                return ident
            draft_pk, ext_key = ident
            conds = [
                TenantFlowPublishVersion.tenant_id == ctx.tenant_id,
            ]
            if draft_pk is not None:
                conds.append(TenantFlowPublishVersion.flow_draft_id == draft_pk)
            else:
                conds.append(TenantFlowPublishVersion.flow_external_key == ext_key)
            if environment is not None:
                conds.append(TenantFlowPublishVersion.environment == environment)

            filt = and_(*conds)

            cnt = await session.scalar(
                select(func.count()).select_from(TenantFlowPublishVersion).where(filt),
            )
            total = int(cnt or 0)

            res = await session.execute(
                select(TenantFlowPublishVersion)
                .where(filt)
                .order_by(TenantFlowPublishVersion.published_at.desc())
                .limit(limit)
                .offset(offset),
            )
            rows = list(res.scalars().all())
        except OperationalError as e:
            _raise_db_unavailable(e)

    return FlowVersionListResponse(
        items=[FlowVersionItemOut.from_row(r) for r in rows],
        limit=limit,
        offset=offset,
        total=total,
    )


@router.get(
    "/me/flows/{flow_id}",
    response_model=FlowDraftDetailOut,
    responses=_RESPONSES_RW,
)
async def get_flow_draft(
    flow_id: uuid.UUID,
    ctx: Annotated[TenantUserContext, Depends(console_flow_editor_context)],
) -> FlowDraftDetailOut:
    settings = get_settings()
    _must_db(settings)
    async with tenant_session(ctx.tenant_id) as session:
        try:
            row = await _get_draft(session, ctx.tenant_id, flow_id)
        except OperationalError as e:
            _raise_db_unavailable(e)
        if row is None:
            raise HTTPException(status_code=404, detail="draft not found")
        return _detail(row)


@router.patch(
    "/me/flows/{flow_id}",
    response_model=FlowDraftDetailOut,
    responses=_RESPONSES_RW,
)
async def patch_flow_draft(
    flow_id: uuid.UUID,
    req: Request,
    ctx: Annotated[TenantUserContext, Depends(console_flow_editor_context)],
    body: FlowDraftPatchBody,
) -> FlowDraftDetailOut | JSONResponse:
    settings = get_settings()
    _must_db(settings)
    async with tenant_session(ctx.tenant_id) as session:
        try:
            row = await _get_draft(session, ctx.tenant_id, flow_id)
        except OperationalError as e:
            _raise_db_unavailable(e)
        if row is None:
            raise HTTPException(status_code=404, detail="draft not found")
        if body.definition is not None:
            val_errs = validate_flow_definition(dict(body.definition))
            if val_errs:
                return _flow_validation_json_response(req, val_errs)
        if body.name is not None:
            row.name = body.name
        if body.definition is not None:
            row.definition = dict(body.definition)
        row.updated_at = _now()
        await session.flush()
        return _detail(row)


@router.post(
    "/me/flows/{flow_id}/publish",
    response_model=FlowPublishResponse,
    responses=_RESPONSES_PUBLISH,
)
async def post_flow_publish(
    req: Request,
    flow_id: Annotated[str, Path(min_length=1, max_length=256)],
    ctx: Annotated[TenantUserContext, Depends(console_flow_editor_context)],
    body: FlowPublishBody,
) -> FlowPublishResponse | JSONResponse:
    """Versao activa por ambiente: snapshot do draft + audit (5.3).

    Uma linha em `tenant_flow_publish_activations` pode ser atualizada quando o
    draft muda (ponteiro para versao activa). Draft por UUID exige sandbox-run
    `succeeded` antes do publish (configuravel); chave `atdd-flow` isenta.
    """
    settings = get_settings()
    _must_db(settings)

    env = body.environment
    if not roles_may_publish_flow(ctx.roles, environment=env):
        raise HTTPException(
            status_code=403,
            detail=(
                "org_admin role required to publish to production"
                if env == "production"
                else "insufficient role to publish to this environment"
            ),
        )

    stripped = flow_id.strip()
    defin: dict[str, Any] | None = None
    draft_pk: uuid.UUID | None = None
    ext_key: str | None = None
    uuid_fid: uuid.UUID | None = None

    if stripped == ATDD_SANDBOX_FLOW_KEY:
        settings_stub = get_settings()
        if not _sandbox_atdd_flow_key_allowed(settings_stub):
            return _flow_validation_json_response(
                req,
                [
                    {
                        "field": "flow_id",
                        "message": (
                            "chave atdd-flow so com AUTH_DEV_STUB ou "
                            "ALLOW_ATDD_SANDBOX_FLOW_KEY=true"
                        ),
                    },
                ],
            )
        defin = dict(_ATDD_SANDBOX_STUB)
        ext_key = ATDD_SANDBOX_FLOW_KEY
    else:
        try:
            uuid_fid = uuid.UUID(stripped)
        except ValueError:
            return _flow_validation_json_response(
                req,
                [
                    {
                        "field": "flow_id",
                        "message": (
                            "use o UUID do rascunho; chave atdd-flow apenas dev/CI "
                            "(stub ou ALLOW_ATDD_SANDBOX_FLOW_KEY)"
                        ),
                    },
                ],
            )

    fp_full: str | None = None
    now = _now()
    act: TenantFlowPublishActivation | None = None

    async with tenant_session(ctx.tenant_id) as session:
        try:
            if uuid_fid is not None:
                row = await _get_draft(session, ctx.tenant_id, uuid_fid)
                if row is None:
                    raise HTTPException(status_code=404, detail="draft not found")
                defin = dict(row.definition or _EMPTY_DEF)
                draft_pk = uuid_fid

            assert defin is not None
            val_errs = validate_flow_definition(defin)
            if val_errs:
                return _flow_validation_json_response(req, val_errs)

            if settings.require_sandbox_success_before_publish and draft_pk is not None:
                n_ok = await session.scalar(
                    select(func.count())
                    .select_from(TenantFlowSandboxRun)
                    .where(
                        TenantFlowSandboxRun.tenant_id == ctx.tenant_id,
                        TenantFlowSandboxRun.flow_draft_id == draft_pk,
                        TenantFlowSandboxRun.status == "succeeded",
                    ),
                )
                if not n_ok:
                    return _flow_validation_json_response(
                        req,
                        [
                            {
                                "field": "flow_id",
                                "message": (
                                    "obrigatorio pelo menos um sandbox-run com "
                                    "sucesso para este rascunho antes de publicar"
                                ),
                            },
                        ],
                    )

            fp_full = _definition_fingerprint_sha256(defin)
            existing = await _get_flow_publish_activation(
                session,
                ctx.tenant_id,
                env,
                draft_id=draft_pk,
                external_key=ext_key,
                for_update=True,
            )
            if existing is not None and existing.definition_fingerprint == fp_full:
                return FlowPublishResponse(
                    activation_id=existing.id,
                    environment=env,
                    flow_draft_id=draft_pk,
                    flow_external_key=ext_key,
                    activated_at=existing.activated_at,
                    idempotent_repeat=True,
                )

            if existing is not None:
                existing.definition_snapshot = defin
                existing.definition_fingerprint = fp_full
                existing.activated_at = now
                existing.activated_by_user_id = ctx.actor_user_id
                act = existing
            else:
                act = TenantFlowPublishActivation(
                    id=uuid.uuid4(),
                    tenant_id=ctx.tenant_id,
                    flow_draft_id=draft_pk,
                    flow_external_key=ext_key,
                    environment=env,
                    definition_snapshot=defin,
                    definition_fingerprint=fp_full,
                    activated_at=now,
                    activated_by_user_id=ctx.actor_user_id,
                )
                session.add(act)

            summary = (
                f"flow_publish env={env} draft_id={draft_pk} ext={ext_key or '-'} "
                f"fp16={fp_full[:16]}"
            )
            session.add(
                AuditEvent(
                    id=uuid.uuid4(),
                    tenant_id=ctx.tenant_id,
                    actor_user_id=ctx.actor_user_id,
                    resource_type="flow_publish",
                    summary=summary[:1024],
                ),
            )
            session.add(
                TenantFlowPublishVersion(
                    id=uuid.uuid4(),
                    tenant_id=ctx.tenant_id,
                    flow_draft_id=draft_pk,
                    flow_external_key=ext_key,
                    environment=env,
                    definition_snapshot=dict(defin),
                    definition_fingerprint=fp_full,
                    published_at=now,
                    published_by_user_id=ctx.actor_user_id,
                    publish_activation_id=act.id,
                ),
            )
            try:
                await session.flush()
            except IntegrityError as exc:
                await session.rollback()
                logger.warning(
                    "publish: IntegrityError (provavel corrida); pedir retry",
                    exc_info=exc,
                )
                raise HTTPException(
                    status_code=409,
                    detail="conflito ao publicar; tente novamente.",
                ) from None
        except OperationalError as e:
            _raise_db_unavailable(e)

    assert act is not None
    return FlowPublishResponse(
        activation_id=act.id,
        environment=env,
        flow_draft_id=draft_pk,
        flow_external_key=ext_key,
        activated_at=act.activated_at,
        idempotent_repeat=False,
    )


@router.post(
    "/me/flows/{flow_id}/sandbox-run",
    response_model=SandboxRunResponse,
    responses=_RESPONSES_SANDBOX,
)
async def post_flow_sandbox_run(
    req: Request,
    flow_id: Annotated[str, Path(min_length=1, max_length=256)],
    ctx: Annotated[TenantUserContext, Depends(console_flow_editor_context)],
    body: SandboxRunBody,
    environment: Annotated[
        str,
        Query(
            description="Obrigatorio sandbox (sem side-effects de producao). "
            "Aceita qualquer capitalizacao (ex. Sandbox).",
        ),
    ] = "sandbox",
) -> SandboxRunResponse | JSONResponse:
    """Preview isolado; nao envia WhatsApp. Chave atdd-flow so com stub/flag explicita.

    Execucao assincrona futura (fila/worker) deve impor o mesmo invariante
    `environment=sandbox` antes de encadear o motor ? nunca simular ou enviar com
    flag de producao.
    """
    if environment.strip().lower() != "sandbox":
        return _flow_validation_json_response(
            req,
            [
                {
                    "field": "environment",
                    "message": "obrigatorio environment=sandbox (execucao nao-prod)",
                },
            ],
        )

    cid = str(getattr(req.state, "request_id", uuid.uuid4()))
    stripped = flow_id.strip()
    definition: dict[str, Any] | None = None
    draft_pk: uuid.UUID | None = None
    ext_key: str | None = None

    if stripped == ATDD_SANDBOX_FLOW_KEY:
        settings_stub = get_settings()
        if not _sandbox_atdd_flow_key_allowed(settings_stub):
            return _flow_validation_json_response(
                req,
                [
                    {
                        "field": "flow_id",
                        "message": (
                            "chave atdd-flow so com AUTH_DEV_STUB ou "
                            "ALLOW_ATDD_SANDBOX_FLOW_KEY=true"
                        ),
                    },
                ],
            )
        definition = dict(_ATDD_SANDBOX_STUB)
        ext_key = ATDD_SANDBOX_FLOW_KEY
    else:
        try:
            fid = uuid.UUID(stripped)
        except ValueError:
            return _flow_validation_json_response(
                req,
                [
                    {
                        "field": "flow_id",
                        "message": (
                            "use o UUID do rascunho; chave atdd-flow apenas dev/CI "
                            "(stub ou ALLOW_ATDD_SANDBOX_FLOW_KEY)"
                        ),
                    },
                ],
            )

        settings = get_settings()
        if not settings.database_url:
            raise HTTPException(status_code=503, detail=_DB_UNAVAILABLE)
        async with tenant_session(ctx.tenant_id) as session:
            try:
                row = await _get_draft(session, ctx.tenant_id, fid)
            except OperationalError as e:
                _raise_db_unavailable(e)
        if row is None:
            raise HTTPException(status_code=404, detail="draft not found")
        definition = dict(row.definition or _EMPTY_DEF)
        draft_pk = fid

    assert definition is not None
    errs = validate_flow_definition(definition)
    if errs:
        return _flow_validation_json_response(req, errs)

    fixture_dict = dict(body.fixture_message)
    settings_fixture = get_settings()
    max_fx = settings_fixture.sandbox_fixture_max_json_bytes
    if _fixture_message_json_bytes(fixture_dict) > max_fx:
        return _flow_validation_json_response(
            req,
            [
                {
                    "field": "fixture_message",
                    "message": (
                        f"fixture JSON excede {max_fx} bytes "
                        "(SANDBOX_FIXTURE_MAX_JSON_BYTES)"
                    ),
                },
            ],
        )

    fp = hashlib.sha256(
        json.dumps(fixture_dict, sort_keys=True, default=str).encode("utf-8"),
    ).hexdigest()[:16]

    status_sim, trace = simulate_sandbox_run(
        definition,
        fixture_dict,
        correlation_id=cid,
        fixture_trace_preview_max=settings_fixture.sandbox_trace_fixture_preview_chars,
    )
    trace = [f"sandbox: fixture_fingerprint_sha256_16={fp}", *trace]

    run_id = uuid.uuid4()
    settings = get_settings()
    persisted = False
    if settings.database_url:
        try:
            async with tenant_session(ctx.tenant_id) as session:
                session.add(
                    TenantFlowSandboxRun(
                        id=run_id,
                        tenant_id=ctx.tenant_id,
                        flow_draft_id=draft_pk,
                        flow_external_key=ext_key,
                        environment="sandbox",
                        fixture=fixture_dict,
                        status=status_sim,
                        trace=trace,
                        correlation_id=cid,
                        created_at=_now(),
                    ),
                )
                await session.flush()
            persisted = True
        except IntegrityError:
            raise
        except SQLAlchemyError:
            logger.warning(
                "sandbox run: persistencia falhou; a devolver trace na mesma "
                "(correlation_id=%s)",
                cid,
                exc_info=True,
            )

    return SandboxRunResponse(
        run_id=run_id,
        status=status_sim,
        environment="sandbox",
        trace=trace,
        correlation_id=cid,
        persisted=persisted,
        fixture_fingerprint=fp,
    )

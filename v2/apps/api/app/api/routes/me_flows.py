"""Rotas fluxos /me: rascunhos (5.1), sandbox preview isolado (5.2).

POST /validate, CRUD drafts, POST sandbox-run (somente environment=sandbox).
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Annotated, Any, Literal

import sqlalchemy.exc as sa_exc
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.errors import (
    CanonicalErrorResponse,
    CanonicalValidationErrorResponse,
    canonical_validation_error_body,
)
from app.db.models_flows import TenantFlowDraft, TenantFlowSandboxRun
from app.db.session import tenant_session
from app.services.flow_sandbox import simulate_sandbox_run
from app.services.flow_validation import validate_flow_definition
from app.tenancy.deps import TenantUserContext, console_flow_editor_context

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
            "examples": [{"fixture_message": {"type": "text", "body": "hi"}}],
        },
    )

    fixture_message: dict[str, Any] = Field(default_factory=dict)


class SandboxRunResponse(BaseModel):
    """Resultado deterministico sandbox; mesmo `run_id` em persistencia opcional."""

    run_id: uuid.UUID
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


_RESPONSES_SANDBOX = {
    200: {"model": SandboxRunResponse},
    401: {"model": CanonicalErrorResponse},
    403: {"model": CanonicalErrorResponse},
    404: {"model": CanonicalErrorResponse},
    422: {"model": CanonicalValidationErrorResponse},
    503: {"model": CanonicalErrorResponse},
}


def _now() -> datetime:
    return datetime.now(UTC)


_EMPTY_DEF: dict[str, Any] = {"nodes": [], "edges": []}


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


def _raise_db_unavailable(exc: sa_exc.OperationalError) -> None:
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
        except sa_exc.OperationalError as e:
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
        except sa_exc.OperationalError as e:
            _raise_db_unavailable(e)
    return _detail(row)


async def _get_draft(session: AsyncSession, fid: uuid.UUID) -> TenantFlowDraft | None:
    res = await session.execute(
        select(TenantFlowDraft).where(TenantFlowDraft.id == fid)
    )
    return res.scalar_one_or_none()


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
            row = await _get_draft(session, flow_id)
        except sa_exc.OperationalError as e:
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
            row = await _get_draft(session, flow_id)
        except sa_exc.OperationalError as e:
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
            description="Obrigatorio sandbox (sem side-effects de producao).",
        ),
    ] = "sandbox",
) -> SandboxRunResponse | JSONResponse:
    """Preview isolado; nao envia WhatsApp. Chave atdd-flow so com stub/flag explicita."""
    if environment != "sandbox":
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
                row = await _get_draft(session, fid)
            except sa_exc.OperationalError as e:
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
    fp = hashlib.sha256(
        json.dumps(fixture_dict, sort_keys=True, default=str).encode("utf-8"),
    ).hexdigest()[:16]

    status_sim, trace = simulate_sandbox_run(
        definition,
        fixture_dict,
        correlation_id=cid,
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
        except sa_exc.OperationalError:
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

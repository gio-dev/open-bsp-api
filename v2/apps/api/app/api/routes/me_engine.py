"""Estado do motor de fluxos (Story 5.5)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.errors import CanonicalErrorResponse
from app.services.flow_engine import parse_flow_engine_environments
from app.tenancy.deps import TenantUserContext, console_tenant_user_context

router = APIRouter(tags=["engine"])


class EngineStatusResponse(BaseModel):
    enabled: bool = Field(description="OPENBSP_FLOW_ENGINE_ENABLED.")
    target_environments: list[str] = Field(
        description="Lista efectiva (OPENBSP_FLOW_ENGINE_ENVIRONMENTS).",
    )
    database_configured: bool = Field(
        description="True se DATABASE_URL definido (motor persistido).",
    )
    policy: str = Field(
        default="NFR-INT-02: idempotencia `engine:{source_id}:{node_id}` em outbound.",
        description="Politica de efeitos repetidos.",
    )


_RESPONSES = {
    200: {"model": EngineStatusResponse},
    401: {"model": CanonicalErrorResponse},
}


@router.get(
    "/me/engine/status",
    response_model=EngineStatusResponse,
    responses=_RESPONSES,
    summary="Estado do motor de fluxos (FR26)",
)
async def get_engine_status(
    ctx: Annotated[TenantUserContext, Depends(console_tenant_user_context)],
) -> EngineStatusResponse:
    _ = ctx.tenant_id
    settings = get_settings()
    envs = sorted(parse_flow_engine_environments(settings))
    db_ok = settings.database_url is not None and len(settings.database_url) > 0
    return EngineStatusResponse(
        enabled=settings.flow_engine_enabled,
        target_environments=envs,
        database_configured=db_ok,
    )

"""FastAPI application entrypoint."""

import asyncio
from contextlib import asynccontextmanager, suppress
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes.auth_oidc import router as auth_oidc_router
from app.api.routes.health import router as health_router
from app.api.routes.me_api_keys import router as me_api_keys_router
from app.api.routes.me_conversations import router as me_conversations_router
from app.api.routes.me_inbox_handoff import router as me_inbox_handoff_router
from app.api.routes.me_inbox_tags import router as me_inbox_tags_router
from app.api.routes.me_members import router as me_members_router
from app.api.routes.me_message_templates import (
    router as me_message_templates_router,
)
from app.api.routes.me_messages import router as me_messages_router
from app.api.routes.me_organization import router as me_org_router
from app.api.routes.me_waba import router as me_waba_router
from app.api.routes.me_webhook_secrets import router as me_webhook_secrets_router
from app.api.routes.webhooks_whatsapp import router as wa_webhook_router
from app.core.config import get_settings
from app.core.errors import (
    canonical_error_body,
    canonical_validation_error_body,
    field_errors_from_request_validation,
)
from app.db.session import reset_engine
from app.whatsapp.outbound_sweep import outbound_sweep_loop


@asynccontextmanager
async def lifespan(_app: FastAPI):
    sweep_task: asyncio.Task[None] | None = None
    settings = get_settings()
    if settings.database_url and settings.outbound_sweep_interval_seconds > 0:
        sweep_task = asyncio.create_task(outbound_sweep_loop())
    try:
        yield
    finally:
        if sweep_task is not None:
            sweep_task.cancel()
            with suppress(asyncio.CancelledError):
                await sweep_task
        await reset_engine()
        get_settings.cache_clear()


def create_app() -> FastAPI:
    application = FastAPI(
        title="Open BSP API",
        version="0.1.0",
        lifespan=lifespan,
        openapi_url="/openapi.json",
        docs_url="/docs",
        openapi_tags=[
            {
                "name": "members",
                "description": (
                    "Membros do tenant (Story 2.2). "
                    "Papeis: org_admin, operator, agent, viewer, finance, support."
                ),
            },
            {
                "name": "webhook-secrets",
                "description": (
                    "Segredo GET hub.verify_token (Meta) por tenant (Story 2.4). "
                    "Rotacao com janela de coexistencia. "
                    "URL: query tenant_id (UUID) para modo tenant."
                ),
            },
            {
                "name": "inbox",
                "description": (
                    "Inbox: conversas, mensagens (4.1), etiquetas (4.2), handoff (4.3)."
                ),
            },
            {
                "name": "messages",
                "description": (
                    "Envio WhatsApp (Story 3.2). Fila persistida; sweep periodico "
                    "(quando OUTBOUND_SWEEP_INTERVAL_SECONDS > 0) reprocessa "
                    "queued/rate_limited; POST tambem dispara entrega em background."
                ),
            },
            {
                "name": "message-templates",
                "description": (
                    "Templates WhatsApp e sinais de canal (Story 3.3). "
                    "GET lista cache; ?refresh=true sincroniza via Graph (org_admin)."
                ),
            },
        ],
    )

    settings = get_settings()
    if settings.console_cors_origin:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[settings.console_cors_origin],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @application.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        rid = request.headers.get("x-request-id") or str(uuid4())
        request.state.request_id = rid
        response = await call_next(request)
        response.headers["x-request-id"] = rid
        return response

    @application.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        rid = getattr(request.state, "request_id", str(uuid4()))
        detail = exc.detail
        message = detail if isinstance(detail, str) else "error"
        return JSONResponse(
            status_code=exc.status_code,
            headers={"x-request-id": rid},
            content=canonical_error_body(
                code=f"http_{exc.status_code}",
                message=message,
                request_id=rid,
            ),
        )

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        rid = getattr(request.state, "request_id", str(uuid4()))
        errors = field_errors_from_request_validation(exc)
        return JSONResponse(
            status_code=422,
            headers={"x-request-id": rid},
            content=canonical_validation_error_body(
                message="validation failed",
                request_id=rid,
                errors=errors,
            ),
        )

    @application.exception_handler(Exception)
    async def generic_exception_handler(request: Request, _exc: Exception):
        rid = getattr(request.state, "request_id", str(uuid4()))
        return JSONResponse(
            status_code=500,
            headers={"x-request-id": rid},
            content=canonical_error_body(
                code="internal_error",
                message="internal server error",
                request_id=rid,
            ),
        )

    application.include_router(health_router, prefix="/v1")
    application.include_router(auth_oidc_router, prefix="/v1")
    application.include_router(me_org_router, prefix="/v1")
    application.include_router(me_conversations_router, prefix="/v1")
    application.include_router(me_inbox_tags_router, prefix="/v1")
    application.include_router(me_inbox_handoff_router, prefix="/v1")
    application.include_router(me_members_router, prefix="/v1")
    application.include_router(me_api_keys_router, prefix="/v1")
    application.include_router(me_webhook_secrets_router, prefix="/v1")
    application.include_router(me_waba_router, prefix="/v1")
    application.include_router(me_message_templates_router, prefix="/v1")
    application.include_router(me_messages_router, prefix="/v1")
    application.include_router(wa_webhook_router, prefix="/v1")
    return application


app = create_app()

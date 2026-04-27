"""FastAPI dependencies: tenant + RBAC (Stories 2.1 / 2.2).

O header ``X-Dev-*`` so com ``AUTH_DEV_STUB=true``. Sem stub, cookie de sessao.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Request

from app.auth.session_cookie import decode_payload
from app.core.config import get_settings
from app.tenancy.rbac import (
    API_KEY_MANAGE_ROLES,
    ORG_WRITE_ROLES,
    VALID_TENANT_ROLES,
    WABA_WRITE_ROLES,
)


def _parse_role_list(raw: str | None) -> set[str]:
    if not raw:
        return set()
    return {p.strip() for p in raw.split(",") if p.strip()}


@dataclass(frozen=True, slots=True)
class TenantUserContext:
    tenant_id: UUID
    actor_user_id: UUID | None
    roles: frozenset[str]


# Alias retrocompat (rotas que exigiam apenas org_admin antes da 2.2)
DevOrgAdminContext = TenantUserContext


def _parse_dev_tenant_user(
    x_dev_tenant_id: str,
    x_dev_roles: str | None,
    x_dev_user_id: str | None,
) -> TenantUserContext:
    roles_raw = _parse_role_list(x_dev_roles)
    # Mesmo filtro que o cookie: so papeis conhecidos (alinhado a producao).
    roles = frozenset(r for r in roles_raw if r in VALID_TENANT_ROLES)
    if not roles:
        raise HTTPException(status_code=403, detail="tenant role required")
    actor: UUID | None = None
    if x_dev_user_id:
        try:
            actor = UUID(x_dev_user_id)
        except ValueError as e:
            raise HTTPException(status_code=403, detail="invalid X-Dev-User-Id") from e
    try:
        tid = UUID(x_dev_tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=403, detail="invalid X-Dev-Tenant-Id") from e
    return TenantUserContext(tenant_id=tid, actor_user_id=actor, roles=roles)


def _session_tenant_user(request: Request) -> TenantUserContext | None:
    settings = get_settings()
    secret = settings.session_signing_secret
    if not secret:
        return None
    raw = request.cookies.get(settings.session_cookie_name)
    if not raw:
        return None
    try:
        payload = decode_payload(raw, secret)
    except ValueError:
        return None
    roles_raw = payload.get("roles") or []
    if not isinstance(roles_raw, list):
        return None
    roles = frozenset(str(r) for r in roles_raw if str(r) in VALID_TENANT_ROLES)
    if not roles:
        return None
    try:
        tid = UUID(str(payload["tid"]))
        uid = UUID(str(payload["uid"]))
    except (KeyError, ValueError):
        return None
    return TenantUserContext(tenant_id=tid, actor_user_id=uid, roles=roles)


async def console_tenant_user_context(
    request: Request,
    x_dev_tenant_id: str | None = Header(default=None, alias="X-Dev-Tenant-Id"),
    x_dev_roles: str | None = Header(default=None, alias="X-Dev-Roles"),
    x_dev_user_id: str | None = Header(default=None, alias="X-Dev-User-Id"),
) -> TenantUserContext:
    settings = get_settings()
    if settings.auth_dev_stub and x_dev_tenant_id:
        return _parse_dev_tenant_user(x_dev_tenant_id, x_dev_roles, x_dev_user_id)
    ctx = _session_tenant_user(request)
    if ctx:
        return ctx
    raise HTTPException(status_code=401, detail="authentication required")


async def console_org_admin_context(
    ctx: Annotated[TenantUserContext, Depends(console_tenant_user_context)],
) -> TenantUserContext:
    if not (ctx.roles & ORG_WRITE_ROLES):
        raise HTTPException(status_code=403, detail="org_admin role required")
    return ctx


async def console_waba_write_context(
    ctx: Annotated[TenantUserContext, Depends(console_tenant_user_context)],
) -> TenantUserContext:
    if not (ctx.roles & WABA_WRITE_ROLES):
        raise HTTPException(status_code=403, detail="org_admin role required")
    return ctx


async def console_api_key_manager_context(
    ctx: Annotated[TenantUserContext, Depends(console_tenant_user_context)],
) -> TenantUserContext:
    if not (ctx.roles & API_KEY_MANAGE_ROLES):
        raise HTTPException(
            status_code=403,
            detail="org_admin or operator role required for api keys",
        )
    return ctx


async def dev_org_admin_context(
    request: Request,
    x_dev_tenant_id: str | None = Header(default=None, alias="X-Dev-Tenant-Id"),
    x_dev_roles: str | None = Header(default=None, alias="X-Dev-Roles"),
    x_dev_user_id: str | None = Header(default=None, alias="X-Dev-User-Id"),
) -> TenantUserContext:
    """Alias retrocompat."""
    ctx = await console_tenant_user_context(
        request, x_dev_tenant_id, x_dev_roles, x_dev_user_id
    )
    if not (ctx.roles & ORG_WRITE_ROLES):
        raise HTTPException(status_code=403, detail="org_admin role required")
    return ctx


async def dev_tenant_id(
    x_dev_tenant_id: str | None = Header(default=None, alias="X-Dev-Tenant-Id"),
) -> UUID:
    """Tenant ativo via stub (rotas legacy)."""
    settings = get_settings()
    if not settings.auth_dev_stub:
        raise HTTPException(
            status_code=403,
            detail="tenant context required",
        )
    if not x_dev_tenant_id:
        raise HTTPException(status_code=403, detail="missing X-Dev-Tenant-Id")
    try:
        return UUID(x_dev_tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=403, detail="invalid X-Dev-Tenant-Id") from e

"""Async engine and session factory with per-transaction RLS GUC."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

if TYPE_CHECKING:
    import uuid

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    global _engine, _session_factory
    from app.core.config import get_settings

    settings = get_settings()
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is not configured")
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url,
            pool_pre_ping=True,
        )
        _session_factory = async_sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _engine


def _get_session_factory() -> async_sessionmaker[AsyncSession]:
    get_engine()
    assert _session_factory is not None
    return _session_factory


@asynccontextmanager
async def platform_session() -> AsyncGenerator[AsyncSession, None]:
    """Sessao sem GUC de tenant (auth / memberships globais)."""
    factory = _get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except BaseException:
            await session.rollback()
            raise


@asynccontextmanager
async def tenant_session(
    tenant_id: "uuid.UUID",
) -> AsyncGenerator[AsyncSession, None]:
    """Session with RLS GUC (set_config ... true => transaction-local).

    O valor e descartado no fim da transacao (seguro com pool async SQLAlchemy).
    Com *transaction pooling* (PgBouncer em modo transaction), garantir que toda
    unidade de trabalho abre transacao, define o GUC e encerra antes de devolver
    a ligacao ao pool; e o padrao deste context manager.
    """
    factory = _get_session_factory()
    async with factory() as session:
        await session.execute(
            text("SELECT set_config('app.tenant_id', :tid, true)"),
            {"tid": str(tenant_id)},
        )
        try:
            yield session
            await session.commit()
        except BaseException:
            await session.rollback()
            raise


async def reset_engine() -> None:
    """Dispose engine (tests)."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None

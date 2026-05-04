"""Parse e resolucao de ambiente do motor (Story 5.5)."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.config import Settings
from app.services.flow_engine import (
    _resolve_runtime_environment,
    parse_flow_engine_environments,
)


def test_parse_flow_engine_environments_default_staging() -> None:
    s = Settings(flow_engine_environments="staging")
    assert parse_flow_engine_environments(s) == frozenset({"staging"})


def test_parse_flow_engine_environments_strips_and_lowercases() -> None:
    s = Settings(flow_engine_environments=" Staging , DEVELOPMENT ")
    assert parse_flow_engine_environments(s) == frozenset({"staging", "development"})


def test_parse_flow_engine_environments_empty_string() -> None:
    s = Settings(flow_engine_environments="")
    assert parse_flow_engine_environments(s) == frozenset()


@pytest.mark.asyncio
async def test_resolve_runtime_environment_no_phone_id() -> None:
    session = MagicMock()
    out = await _resolve_runtime_environment(
        session,
        uuid.uuid4(),
        None,
    )
    assert out is None
    session.scalar.assert_not_called()


@pytest.mark.asyncio
async def test_resolve_runtime_environment_unknown_phone() -> None:
    session = MagicMock()
    session.scalar = AsyncMock(return_value=None)
    out = await _resolve_runtime_environment(
        session,
        uuid.uuid4(),
        "nonexistent-pnid",
    )
    assert out is None

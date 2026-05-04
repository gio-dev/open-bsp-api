"""Unit: derivacao modo bot/humano (Story 6.2)."""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from app.inbox.conversation_mode import conversation_mode_and_since

T0 = datetime(2026, 4, 24, 12, 0, tzinfo=timezone.utc)
T1 = datetime(2026, 4, 24, 13, 0, tzinfo=timezone.utc)
T2 = datetime(2026, 4, 24, 14, 0, tzinfo=timezone.utc)


def _conv(**kw):
    return SimpleNamespace(
        last_activity_at=kw.get("last_activity_at", T1),
        updated_at=kw.get("updated_at", T1),
        created_at=kw.get("created_at", T0),
    )


@pytest.mark.parametrize(
    "state",
    ("pending_handoff", "queued", "accepted", "failed"),
)
def test_human_pipeline_states_use_handoff_updated_at(state: str) -> None:
    conv = _conv()
    ho = SimpleNamespace(handoff_state=state, updated_at=T2)
    mode, since = conversation_mode_and_since(conv=conv, handoff=ho)
    assert mode == "human_active"
    assert since == T2


def test_automated_is_bot_uses_handoff_timestamp_when_present() -> None:
    conv = _conv()
    ho = SimpleNamespace(handoff_state="automated", updated_at=T2)
    mode, since = conversation_mode_and_since(conv=conv, handoff=ho)
    assert mode == "bot_active"
    assert since == T2


def test_no_handoff_is_bot_uses_activity_fallback() -> None:
    conv = _conv()
    mode, since = conversation_mode_and_since(conv=conv, handoff=None)
    assert mode == "bot_active"
    assert since == conv.last_activity_at


def test_invalid_handoff_state_treated_as_automated_bot() -> None:
    conv = _conv()
    ho = SimpleNamespace(handoff_state="unknown_state", updated_at=T2)
    mode, since = conversation_mode_and_since(conv=conv, handoff=ho)
    assert mode == "bot_active"
    assert since == T2


def test_bot_fallback_chain_without_handoff_timestamps() -> None:
    conv = SimpleNamespace(last_activity_at=None, updated_at=None, created_at=T0)
    ho = SimpleNamespace(handoff_state="automated", updated_at=None)
    mode, since = conversation_mode_and_since(conv=conv, handoff=ho)
    assert mode == "bot_active"
    assert since == T0

"""Unit: gates de preferencias outbound (Story 6.3)."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest

from app.contacts.outbound_prefs import outbound_preference_violation


@pytest.mark.asyncio
async def test_outbound_preference_violation_non_digit_recipient() -> None:
    session = AsyncMock()
    v = await outbound_preference_violation(
        session,
        uuid.uuid4(),
        contact_key_digits="not-digits",
        preference_kind="marketing",
    )
    assert v == "invalid_recipient_for_preference_kind"
    session.scalar.assert_not_called()


@pytest.mark.asyncio
async def test_outbound_preference_violation_none_skips_db() -> None:
    session = AsyncMock()
    v = await outbound_preference_violation(
        session,
        uuid.uuid4(),
        contact_key_digits="anything",
        preference_kind="none",
    )
    assert v is None
    session.scalar.assert_not_called()

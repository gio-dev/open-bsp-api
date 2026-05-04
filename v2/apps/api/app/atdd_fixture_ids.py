"""Identificadores de fixtures ATDD/CI alinhados a `derived_conversation_id` (4.1)."""

from __future__ import annotations

from uuid import UUID

from app.inbox.sync import derived_conversation_id

ATDD_TENANT_ID = UUID("11111111-1111-4111-8111-111111111111")

# Mesmo (tenant, waba, contact) que o seed de inbox; PK = hash estavel.
ATDD_INBOX_CONVERSATION_ID: str = derived_conversation_id(
    ATDD_TENANT_ID,
    "ci-atdd-waba",
    "15550009999",
)

# Fixture Story 6.3 (preferences path seg mento URL).
ATDD_CONTACT_PREFERENCES_ID: str = "atdd-contact"

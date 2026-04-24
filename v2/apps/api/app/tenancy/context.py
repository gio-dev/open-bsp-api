"""Tenant execution context (Story 1.2).

RLS uses PostgreSQL GUC ``app.tenant_id``. Set per transaction in
``tenant_session`` via ``set_config(..., true)`` (transaction-local; pool-safe).
"""

from uuid import UUID

# Re-export for callers documenting tenant source
TenantId = UUID

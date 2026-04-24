"""Shared fixtures for Epic 1 ATDD tests."""

import pytest


@pytest.fixture
def atdd_dev_headers() -> dict[str, str]:
    """Dev stub headers (Story 1.3 VS). Remove when OAuth (2.1) is active."""
    return {
        "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
        "X-Dev-User-Id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        "X-Dev-Roles": "org_admin",
    }

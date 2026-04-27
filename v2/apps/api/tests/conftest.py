import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("AUTH_DEV_STUB", "true")
os.environ.setdefault("WHATSAPP_WEBHOOK_VERIFY_TOKEN", "atdd-verify")
os.environ.setdefault("SESSION_SIGNING_SECRET", "test-session-secret-atdd")
# Opcional: OPENBSP_SKIP_API_KEY_CREATE_THROTTLE=1,
#           OPENBSP_SKIP_WEBHOOK_ROTATE_THROTTLE=1 (testes de taxa/429 manuais).

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """One ASGI loop for the suite: global async engine stays loop-consistent."""
    with TestClient(app) as test_client:
        yield test_client

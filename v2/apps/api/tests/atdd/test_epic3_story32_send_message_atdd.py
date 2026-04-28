"""ATDD Story 3.2 - Envio mensagem saida, fila, retry (RED until DS)."""

import os

import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.atdd, pytest.mark.epic3_atdd]


@pytest.mark.atdd
@pytest.mark.skipif(
    not os.getenv("DATABASE_URL"),
    reason="envio persiste estado em Postgres (CI api-ci)",
)
def test_story_32_post_send_message_returns_accepted_state(client: TestClient):
    """3.2: send creates persisted accepted/pending state."""
    r = client.post(
        "/v1/me/messages/send",
        headers={
            "X-Dev-Tenant-Id": "11111111-1111-4111-8111-111111111111",
            "X-Dev-Roles": "org_admin",
        },
        json={
            "to": "+351910000099",
            "type": "text",
            "text": {"body": "atdd"},
            "environment": "sandbox",
        },
    )
    assert r.status_code in (200, 201, 202), r.text
    data = r.json()
    assert "status" in data or "id" in data

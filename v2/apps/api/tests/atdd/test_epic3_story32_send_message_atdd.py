"""ATDD Story 3.2 - Envio mensagem saida, fila, retry (RED until DS)."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.atdd
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
        },
    )
    assert r.status_code in (200, 201, 202), r.text
    assert "status" in r.json() or "id" in r.json()

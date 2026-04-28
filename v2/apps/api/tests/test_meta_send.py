"""Meta send helpers (Story 3.2)."""

import httpx
import pytest
from app.core.config import Settings
from app.whatsapp.meta_send import (
    MetaSendResult,
    normalize_whatsapp_to,
    send_whatsapp_text,
)


def test_normalize_whatsapp_to_strips_plus() -> None:
    assert normalize_whatsapp_to("+351 910 000 099") == "351910000099"


def test_normalize_whatsapp_to_rejects_invalid() -> None:
    with pytest.raises(ValueError):
        normalize_whatsapp_to("abc")


def test_meta_send_result_ok() -> None:
    r = MetaSendResult(ok=True, meta_message_id="x")
    assert r.ok


@pytest.mark.asyncio
async def test_send_200_without_message_id_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeResponse:
        status_code = 200
        text = ""

        def json(self) -> dict:
            return {"messages": [{"preview": False}]}

    class FakeClient:
        async def post(self, *args, **kwargs):
            return FakeResponse()

        async def aclose(self) -> None:
            return None

    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: FakeClient())
    s = Settings(whatsapp_cloud_access_token="t", whatsapp_cloud_api_stub=False)
    r = await send_whatsapp_text(
        phone_number_id="123456789",
        to_digits="351910000099",
        body="hi",
        settings=s,
    )
    assert not r.ok
    assert r.error_code == "missing_message_id"

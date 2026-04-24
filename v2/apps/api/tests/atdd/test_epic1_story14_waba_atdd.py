"""ATDD Story 1.4 - WABA, numbers, environments (FR2, FR4)."""

import uuid

import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.atdd, pytest.mark.epic1_atdd]


@pytest.mark.atdd
def test_story_14_post_waba_phone_association_returns_201(
    client: TestClient,
    atdd_dev_headers: dict[str, str],
):
    suf = uuid.uuid4().hex[:10]
    payload = {
        "waba_id": f"waba_atdd_{suf}",
        "phone_number_id": f"pn_atdd_{suf}",
        "display_phone_number": "+351910000001",
        "environment": "production",
    }
    r = client.post(
        "/v1/me/waba-phone-numbers",
        headers=atdd_dev_headers,
        json=payload,
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body.get("status") in ("active", "pending", "suspended")
    assert body.get("environment") == "production"


@pytest.mark.atdd
def test_story_14_post_defaults_environment_to_production(
    client: TestClient,
    atdd_dev_headers: dict[str, str],
):
    suf = uuid.uuid4().hex[:10]
    r = client.post(
        "/v1/me/waba-phone-numbers",
        headers=atdd_dev_headers,
        json={
            "waba_id": f"waba_def_{suf}",
            "phone_number_id": f"pn_def_{suf}",
            "display_phone_number": "+351910000099",
        },
    )
    assert r.status_code == 201, r.text
    assert r.json().get("environment") == "production"


@pytest.mark.atdd
def test_story_14_duplicate_post_returns_409(
    client: TestClient,
    atdd_dev_headers: dict[str, str],
):
    suf = uuid.uuid4().hex[:10]
    payload = {
        "waba_id": f"waba_dup_{suf}",
        "phone_number_id": f"pn_dup_{suf}",
        "display_phone_number": "+351910000002",
        "environment": "production",
    }
    assert (
        client.post(
            "/v1/me/waba-phone-numbers",
            headers=atdd_dev_headers,
            json=payload,
        ).status_code
        == 201
    )
    r2 = client.post(
        "/v1/me/waba-phone-numbers",
        headers=atdd_dev_headers,
        json=payload,
    )
    assert r2.status_code == 409, r2.text


@pytest.mark.atdd
def test_story_14_list_waba_filtered_by_environment(
    client: TestClient,
    atdd_dev_headers: dict[str, str],
):
    r = client.get(
        "/v1/me/waba-phone-numbers",
        headers={**atdd_dev_headers, "X-Environment": "production"},
        params={"environment": "production"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    items = data if isinstance(data, list) else data.get("items", [])
    for item in items:
        assert item.get("environment") == "production", item


@pytest.mark.atdd
def test_story_14_development_rows_hidden_from_production_list(
    client: TestClient,
    atdd_dev_headers: dict[str, str],
):
    suf = uuid.uuid4().hex[:10]
    dev_payload = {
        "waba_id": f"waba_atdd_dev_{suf}",
        "phone_number_id": f"pn_atdd_dev_{suf}",
        "display_phone_number": "+351920000002",
        "environment": "development",
    }
    c_dev = client.post(
        "/v1/me/waba-phone-numbers",
        headers=atdd_dev_headers,
        json=dev_payload,
    )
    assert c_dev.status_code == 201, c_dev.text

    r = client.get(
        "/v1/me/waba-phone-numbers",
        headers={**atdd_dev_headers, "X-Environment": "production"},
        params={"environment": "production"},
    )
    assert r.status_code == 200
    body = r.json()
    lst = body if isinstance(body, list) else body.get("items", [])
    ids = {i.get("phone_number_id") for i in lst}
    assert dev_payload["phone_number_id"] not in ids, lst


@pytest.mark.atdd
def test_story_14_patch_status(client: TestClient, atdd_dev_headers: dict[str, str]):
    suf = uuid.uuid4().hex[:10]
    c = client.post(
        "/v1/me/waba-phone-numbers",
        headers=atdd_dev_headers,
        json={
            "waba_id": f"waba_patch_{suf}",
            "phone_number_id": f"pn_patch_{suf}",
            "display_phone_number": "+351930000003",
            "environment": "staging",
        },
    )
    assert c.status_code == 201, c.text
    row_id = c.json()["id"]
    p = client.patch(
        f"/v1/me/waba-phone-numbers/{row_id}",
        headers=atdd_dev_headers,
        json={"status": "active"},
    )
    assert p.status_code == 200, p.text
    assert p.json().get("status") == "active"

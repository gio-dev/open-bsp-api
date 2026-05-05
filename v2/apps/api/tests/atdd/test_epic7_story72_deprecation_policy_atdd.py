"""ATDD Story 7.2: politica publica de ciclo de vida e deprecacao (FR37)."""

import pytest

pytestmark = [pytest.mark.atdd, pytest.mark.epic7_atdd]


@pytest.mark.atdd
def test_story_72_deprecation_policy_json(client):
    """7.2: `/v1/policy/deprecation` devolve JSON alinhado ao OpenAPI."""
    r = client.get("/v1/policy/deprecation")
    assert r.status_code == 200, r.text
    body = r.json()

    spec = client.get("/openapi.json").json()
    assert body["api_semantic_version"] == spec["info"]["version"]
    assert body["rest_stable_prefix"] == "/v1"
    assert body["openapi_url_path"] == "/openapi.json"

    for key in (
        "policy_summary",
        "deprecation_http_headers",
        "changelog_reference",
        "coexistence_window_days_guideline",
        "deprecation_entries",
    ):
        assert key in body, body

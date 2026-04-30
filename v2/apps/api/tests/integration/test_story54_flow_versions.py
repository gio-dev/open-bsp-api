"""Story 5.4: GET .../versions e detalhe com snapshot material (Postgres CI)."""

from __future__ import annotations

import os
import uuid

import psycopg
import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL") or not os.getenv("ALEMBIC_SYNC_URL"),
    reason="needs DATABASE_URL and ALEMBIC_SYNC_URL (CI postgres)",
)

TENANT = "11111111-1111-4111-8111-111111111111"
_HDR_OP = {"X-Dev-Tenant-Id": TENANT, "X-Dev-Roles": "operator"}


def _graph_v1() -> dict:
    return {
        "nodes": [
            {"id": "t_v54", "kind": "trigger"},
            {"id": "a_v54", "kind": "action"},
        ],
        "edges": [{"source": "t_v54", "target": "a_v54"}],
    }


def _graph_v2() -> dict:
    return {
        "nodes": [
            {"id": "t_v54", "kind": "trigger"},
            {"id": "a_v54", "kind": "action"},
            {"id": "x_v54", "kind": "action"},
        ],
        "edges": [
            {"source": "t_v54", "target": "a_v54"},
            {"source": "a_v54", "target": "x_v54"},
        ],
    }


def _sandbox_ok(client: TestClient, flow_id: str) -> None:
    r = client.post(
        f"/v1/me/flows/{flow_id}/sandbox-run",
        headers=_HDR_OP,
        params={"environment": "sandbox"},
        json={"fixture_message": {"type": "text", "body": "v54"}},
    )
    assert r.status_code == 200, r.text


@pytest.mark.integration
def test_versions_list_detail_after_publish(client: TestClient) -> None:
    name = f"v54-{uuid.uuid4().hex[:8]}"
    r = client.post(
        "/v1/me/flows",
        headers=_HDR_OP,
        json={"name": name, "definition": _graph_v1()},
    )
    assert r.status_code == 201, r.text
    fid = r.json()["id"]
    _sandbox_ok(client, fid)
    rp = client.post(
        f"/v1/me/flows/{fid}/publish",
        headers=_HDR_OP,
        json={"environment": "staging"},
    )
    assert rp.status_code == 200, rp.text

    rl = client.get(
        f"/v1/me/flows/{fid}/versions",
        headers=_HDR_OP,
        params={"limit": 10, "offset": 0},
    )
    assert rl.status_code == 200, rl.text
    body = rl.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    item = body["items"][0]
    vid = item["version_id"]
    assert item["environment"] == "staging"
    assert len(item["definition_fingerprint"]) == 64
    assert item["definition_fingerprint_prefix"] == item["definition_fingerprint"][:16]

    rd = client.get(f"/v1/me/flows/{fid}/versions/{vid}", headers=_HDR_OP)
    assert rd.status_code == 200, rd.text
    detail = rd.json()
    assert detail["version_id"] == vid
    assert detail["definition"]["nodes"][0]["id"] == "t_v54"


@pytest.mark.integration
def test_versions_ordered_newest_first_pagination_total(client: TestClient) -> None:
    admin_url = os.environ["ALEMBIC_SYNC_URL"]
    name = f"v54p-{uuid.uuid4().hex[:8]}"
    r = client.post(
        "/v1/me/flows",
        headers=_HDR_OP,
        json={"name": name, "definition": _graph_v1()},
    )
    assert r.status_code == 201, r.text
    fid = r.json()["id"]
    _sandbox_ok(client, fid)
    rp1 = client.post(
        f"/v1/me/flows/{fid}/publish",
        headers=_HDR_OP,
        json={"environment": "development"},
    )
    assert rp1.status_code == 200, rp1.text

    r_patch = client.patch(
        f"/v1/me/flows/{fid}",
        headers=_HDR_OP,
        json={"definition": _graph_v2()},
    )
    assert r_patch.status_code == 200, r_patch.text
    _sandbox_ok(client, fid)
    rp2 = client.post(
        f"/v1/me/flows/{fid}/publish",
        headers=_HDR_OP,
        json={"environment": "development"},
    )
    assert rp2.status_code == 200, rp2.text

    rl = client.get(
        f"/v1/me/flows/{fid}/versions",
        headers=_HDR_OP,
        params={
            "environment": "development",
            "limit": 1,
            "offset": 0,
        },
    )
    assert rl.status_code == 200, rl.text
    b0 = rl.json()
    assert b0["total"] == 2
    assert len(b0["items"]) == 1
    vid_newest = b0["items"][0]["version_id"]

    rl2 = client.get(
        f"/v1/me/flows/{fid}/versions",
        headers=_HDR_OP,
        params={"environment": "development", "limit": 99, "offset": 1},
    )
    assert rl2.status_code == 200, rl2.text
    b1 = rl2.json()
    assert b1["total"] == 2
    assert len(b1["items"]) == 1
    vid_older = b1["items"][0]["version_id"]

    assert vid_newest != vid_older

    dn = client.get(f"/v1/me/flows/{fid}/versions/{vid_newest}", headers=_HDR_OP).json()
    assert len(dn["definition"]["nodes"]) == 3
    do = client.get(f"/v1/me/flows/{fid}/versions/{vid_older}", headers=_HDR_OP).json()
    assert len(do["definition"]["nodes"]) == 2

    with psycopg.connect(admin_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                (
                    "SELECT published_at FROM tenant_flow_publish_versions "
                    "WHERE id = %s::uuid"
                ),
                (vid_newest,),
            )
            ts_new = cur.fetchone()[0]
            cur.execute(
                (
                    "SELECT published_at FROM tenant_flow_publish_versions "
                    "WHERE id = %s::uuid"
                ),
                (vid_older,),
            )
            ts_old = cur.fetchone()[0]
    assert ts_new >= ts_old

    fake_vid = uuid.uuid4()
    r404 = client.get(
        f"/v1/me/flows/{fid}/versions/{fake_vid}",
        headers=_HDR_OP,
    )
    assert r404.status_code == 404, r404.text

"""Unit tests sandbox simulation (Story 5.2)."""

from app.services.flow_sandbox import simulate_sandbox_run


def test_simulate_matches_minimal_valid_graph() -> None:
    definition = {
        "nodes": [
            {"id": "t", "kind": "trigger"},
            {"id": "a", "kind": "action"},
        ],
        "edges": [{"source": "t", "target": "a"}],
    }
    fx = {"type": "text", "body": "hi"}
    status, trace = simulate_sandbox_run(definition, fx, correlation_id="cid-1")
    assert status == "succeeded"
    assert any("sandbox" in x for x in trace)
    assert any("never production WhatsApp" in x or "Meta send" in x for x in trace)
    assert any("fixture_message=" in x for x in trace)


def test_diamond_converges_single_action_visit() -> None:
    """BFS: dois ramos para o mesmo action visita action uma vez; preview simplificado."""
    definition = {
        "nodes": [
            {"id": "t1", "kind": "trigger"},
            {"id": "c1", "kind": "condition"},
            {"id": "c2", "kind": "condition"},
            {"id": "a1", "kind": "action"},
        ],
        "edges": [
            {"source": "t1", "target": "c1"},
            {"source": "t1", "target": "c2"},
            {"source": "c1", "target": "a1"},
            {"source": "c2", "target": "a1"},
        ],
    }
    status, trace = simulate_sandbox_run(
        definition,
        {"type": "text"},
        correlation_id="cid-diamond",
    )
    assert status == "succeeded"
    action_hits = [x for x in trace if "node a1 (action)" in x]
    assert len(action_hits) == 1

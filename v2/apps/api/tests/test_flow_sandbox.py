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
    """BFS: dois ramos ao mesmo action; action visitada uma vez (preview)."""
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


def test_simulate_aborts_when_edge_targets_missing_node() -> None:
    """Defensivo: grafo inconsistente (ex. chamada direta sem validador 5.1)."""
    definition = {
        "nodes": [
            {"id": "t", "kind": "trigger"},
            {"id": "a", "kind": "action"},
        ],
        "edges": [{"source": "t", "target": "fantasma"}],
    }
    status, trace = simulate_sandbox_run(
        definition,
        {},
        correlation_id="cid-missing",
    )
    assert status == "failed"
    assert any("fantasma" in x and "ausente" in x for x in trace)


def test_fixture_preview_truncates_in_trace() -> None:
    long_body = "x" * 2000
    definition = {
        "nodes": [
            {"id": "t", "kind": "trigger"},
            {"id": "a", "kind": "action"},
        ],
        "edges": [{"source": "t", "target": "a"}],
    }
    fx = {"type": "text", "body": long_body}
    _st, trace = simulate_sandbox_run(
        definition,
        fx,
        correlation_id="cid-trunc",
        fixture_trace_preview_max=120,
    )
    line = next(x for x in trace if x.startswith("sandbox: fixture_message="))
    assert "truncado para log" in line
    assert "chars" in line

"""Unit tests para validacao estrutural de fluxos (Story 5.1)."""

from app.services.flow_validation import (
    MAX_FLOW_NODES,
    FlowGraphPayload,
    coerce_flow_definition,
    validate_flow_structure,
)


def test_valid_simple_flow() -> None:
    graph = FlowGraphPayload.model_validate(
        {
            "nodes": [
                {"id": "t1", "kind": "trigger"},
                {"id": "a1", "kind": "action"},
            ],
            "edges": [{"source": "t1", "target": "a1"}],
        }
    )
    assert validate_flow_structure(graph) == []


def test_empty_nodes_rejected() -> None:
    graph = FlowGraphPayload.model_validate({"nodes": [], "edges": []})
    errs = validate_flow_structure(graph)
    assert any(e["field"] == "nodes" for e in errs)


def test_must_have_exactly_one_trigger() -> None:
    graph = FlowGraphPayload.model_validate(
        {
            "nodes": [
                {"id": "t1", "kind": "trigger"},
                {"id": "t2", "kind": "trigger"},
                {"id": "a1", "kind": "action"},
            ],
            "edges": [{"source": "t1", "target": "a1"}],
        }
    )
    errs = validate_flow_structure(graph)
    assert errs and errs[0]["field"] == "nodes"


def test_cycle_detected() -> None:
    graph = FlowGraphPayload.model_validate(
        {
            "nodes": [
                {"id": "t1", "kind": "trigger"},
                {"id": "c1", "kind": "condition"},
                {"id": "a1", "kind": "action"},
            ],
            "edges": [
                {"source": "t1", "target": "c1"},
                {"source": "c1", "target": "a1"},
                {"source": "a1", "target": "c1"},
            ],
        }
    )
    errs = validate_flow_structure(graph)
    assert any("ciclo" in e["message"].lower() for e in errs)


def test_max_nodes_gate() -> None:
    n_max = MAX_FLOW_NODES + 1
    ids = [{"id": f"n{i}", "kind": "action" if i else "trigger"} for i in range(n_max)]
    edges = [
        {"source": ids[i]["id"], "target": ids[i + 1]["id"]}
        for i in range(MAX_FLOW_NODES)
    ]
    graph = FlowGraphPayload.model_validate({"nodes": ids, "edges": edges})
    errs = validate_flow_structure(graph)
    assert any(
        "limite" in e["message"].lower() or "maximo" in e["message"].lower()
        for e in errs
    )


def test_unknown_edge_endpoint() -> None:
    graph = FlowGraphPayload.model_validate(
        {
            "nodes": [
                {"id": "t1", "kind": "trigger"},
                {"id": "a1", "kind": "action"},
            ],
            "edges": [{"source": "t1", "target": "missing"}],
        }
    )
    errs = validate_flow_structure(graph)
    assert errs


def test_unreachable_node_one_issue_per_id() -> None:
    graph = FlowGraphPayload.model_validate(
        {
            "nodes": [
                {"id": "t1", "kind": "trigger"},
                {"id": "a1", "kind": "action"},
                {"id": "orphan", "kind": "action"},
            ],
            "edges": [{"source": "t1", "target": "a1"}],
        }
    )
    errs = validate_flow_structure(graph)
    assert any(e["field"] == "nodes.orphan" for e in errs)


def test_coerce_rejects_extra_field_on_node() -> None:
    graph, errs = coerce_flow_definition(
        {
            "nodes": [{"id": "t1", "kind": "trigger", "typo_field": 1}],
            "edges": [],
        },
    )
    assert graph is None
    assert errs


def test_coerce_rejects_bad_node_kind() -> None:
    graph, errs = coerce_flow_definition(
        {
            "nodes": [{"id": "t1", "kind": "llm_trigger"}],
            "edges": [],
        },
    )
    assert graph is None and errs


def test_structure_rejects_missing_edge_target_node() -> None:
    graph = FlowGraphPayload.model_validate(
        {
            "nodes": [
                {"id": "t1", "kind": "trigger"},
                {"id": "a1", "kind": "action"},
            ],
            "edges": [{"source": "t1", "target": "ghost"}],
        }
    )
    errs = validate_flow_structure(graph)
    assert any("ghost" in e["message"] for e in errs)

"""Unit tests para validacao estrutural de fluxos (Story 5.1)."""

from app.services.flow_validation import (
    MAX_FLOW_NODES,
    FlowGraphPayload,
    coerce_flow_definition,
    validate_flow_structure,
)


def test_send_text_requires_body_when_action_type_set() -> None:
    graph = FlowGraphPayload.model_validate(
        {
            "nodes": [
                {"id": "t1", "kind": "trigger"},
                {
                    "id": "a1",
                    "kind": "action",
                    "action_type": "send_text",
                    "text_body": "",
                },
            ],
            "edges": [{"source": "t1", "target": "a1"}],
        }
    )
    errs = validate_flow_structure(graph)
    assert any(e["field"] == "nodes.a1.text_body" for e in errs)


def test_valid_simple_flow() -> None:
    graph = FlowGraphPayload.model_validate(
        {
            "nodes": [
                {"id": "t1", "kind": "trigger"},
                {
                    "id": "a1",
                    "kind": "action",
                    "action_type": "send_text",
                    "text_body": "x",
                },
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


def test_rejects_marketing_send_without_update_preferences_on_path() -> None:
    graph = FlowGraphPayload.model_validate(
        {
            "nodes": [
                {"id": "t1", "kind": "trigger"},
                {
                    "id": "a1",
                    "kind": "action",
                    "action_type": "send_text",
                    "text_body": "promo",
                    "preference_kind": "marketing",
                },
            ],
            "edges": [{"source": "t1", "target": "a1"}],
        }
    )
    errs = validate_flow_structure(graph)
    assert any("update_preferences" in e["message"] for e in errs)


def test_rejects_diamond_bypassing_prefs_before_marketing() -> None:
    graph = FlowGraphPayload.model_validate(
        {
            "nodes": [
                {"id": "t1", "kind": "trigger"},
                {
                    "id": "p1",
                    "kind": "action",
                    "action_type": "update_preferences",
                    "marketing_opt_in": True,
                    "disclosure_copy_slug": "x",
                },
                {"id": "b1", "kind": "condition"},
                {
                    "id": "a1",
                    "kind": "action",
                    "action_type": "send_text",
                    "text_body": "m",
                    "preference_kind": "marketing",
                },
            ],
            "edges": [
                {"source": "t1", "target": "p1"},
                {"source": "t1", "target": "b1"},
                {"source": "p1", "target": "a1"},
                {"source": "b1", "target": "a1"},
            ],
        }
    )
    errs = validate_flow_structure(graph)
    assert any("6.3" in e["message"] for e in errs)


def test_valid_flow_with_consent_then_marketing_send_text() -> None:
    graph = FlowGraphPayload.model_validate(
        {
            "nodes": [
                {"id": "t1", "kind": "trigger"},
                {
                    "id": "p1",
                    "kind": "action",
                    "action_type": "update_preferences",
                    "marketing_opt_in": True,
                    "disclosure_copy_slug": "v-flow",
                },
                {
                    "id": "a1",
                    "kind": "action",
                    "action_type": "send_text",
                    "text_body": "hello",
                    "preference_kind": "marketing",
                },
            ],
            "edges": [
                {"source": "t1", "target": "p1"},
                {"source": "p1", "target": "a1"},
            ],
        }
    )
    assert validate_flow_structure(graph) == []


def test_update_preferences_requires_at_least_one_field() -> None:
    graph = FlowGraphPayload.model_validate(
        {
            "nodes": [
                {"id": "t1", "kind": "trigger"},
                {
                    "id": "p1",
                    "kind": "action",
                    "action_type": "update_preferences",
                },
            ],
            "edges": [{"source": "t1", "target": "p1"}],
        }
    )
    errs = validate_flow_structure(graph)
    assert any("update_preferences" in e["message"] for e in errs)


def test_coerce_rejects_preference_fields_on_send_text_node() -> None:
    _, errs = coerce_flow_definition(
        {
            "nodes": [
                {"id": "t1", "kind": "trigger"},
                {
                    "id": "a1",
                    "kind": "action",
                    "action_type": "send_text",
                    "text_body": "x",
                    "marketing_opt_in": True,
                },
            ],
            "edges": [{"source": "t1", "target": "a1"}],
        },
    )
    assert errs


def test_coerce_rejects_preference_kind_on_update_preferences() -> None:
    _, errs = coerce_flow_definition(
        {
            "nodes": [
                {"id": "t1", "kind": "trigger"},
                {
                    "id": "p1",
                    "kind": "action",
                    "action_type": "update_preferences",
                    "marketing_opt_in": True,
                    "preference_kind": "marketing",
                },
            ],
            "edges": [{"source": "t1", "target": "p1"}],
        },
    )
    assert errs


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

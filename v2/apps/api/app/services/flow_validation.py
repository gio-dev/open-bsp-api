"""Validacao estrutural de grafos de fluxo (Story 5.1)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

MAX_FLOW_NODES = 200


class FlowNodePayload(BaseModel):
    """Um no rule-based (trigger|condition|acao)."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=128)
    kind: str = Field(
        ...,
        examples=["trigger", "condition", "action"],
    )

    @field_validator("kind")
    @classmethod
    def _kind_ok(cls, v: str) -> str:
        if v not in ("trigger", "condition", "action"):
            msg = 'kind deve ser trigger, condition ou action (recebido "{}")'
            raise ValueError(msg.format(v))
        return v


class FlowEdgePayload(BaseModel):
    """Aresta orientada."""

    model_config = ConfigDict(extra="forbid")

    source: str = Field(min_length=1, max_length=128)
    target: str = Field(min_length=1, max_length=128)
    id: str | None = Field(default=None, max_length=128)


class FlowGraphPayload(BaseModel):
    nodes: list[FlowNodePayload] = Field(default_factory=list)
    edges: list[FlowEdgePayload] = Field(default_factory=list)


def coerce_flow_definition(
    raw: dict,
) -> tuple[FlowGraphPayload | None, list[dict[str, str]]]:
    """Valida Pydantic; devolve (grafico,[]) ou (None, erros campo/mensagem)."""
    try:
        payload = FlowGraphPayload.model_validate(raw)
    except ValidationError as exc:
        out: list[dict[str, str]] = []
        for err in exc.errors():
            loc = err.get("loc") or ()
            tail = ".".join(str(x) for x in loc) if loc else "body"
            out.append({"field": tail, "message": str(err.get("msg", "invalid"))})
        return None, out
    return payload, []


def validate_flow_structure(graph: FlowGraphPayload) -> list[dict[str, str]]:
    """Regras de dominio sobre o grafo parseado."""
    errs: list[dict[str, str]] = []
    nodes = graph.nodes
    edges = graph.edges

    if not nodes:
        errs.append(
            {"field": "nodes", "message": "o fluxo deve ter pelo menos um no"},
        )
        return errs

    if len(nodes) > MAX_FLOW_NODES:
        errs.append(
            {
                "field": "nodes",
                "message": f"limite maximo de {MAX_FLOW_NODES} nos",
            },
        )
        return errs

    by_id = {n.id: n for n in nodes}
    if len(by_id) != len(nodes):
        errs.append({"field": "nodes", "message": "existem ids de nos duplicados"})
        return errs

    triggers = [n for n in nodes if n.kind == "trigger"]
    if len(triggers) != 1:
        errs.append(
            {
                "field": "nodes",
                "message": (
                    "e obrigatorio exatamente um no do tipo trigger; "
                    f"encontrados {len(triggers)}"
                ),
            },
        )
        return errs

    trigger_id = triggers[0].id
    for ei, edge in enumerate(edges):
        if edge.target == trigger_id:
            errs.append(
                {
                    "field": f"edges[{ei}].target",
                    "message": "o no trigger nao pode ter arestas de entrada",
                },
            )

    if errs:
        return errs

    for ei, edge in enumerate(edges):
        if edge.source not in by_id:
            errs.append(
                {
                    "field": f"edges[{ei}].source",
                    "message": f'no "{edge.source}" nao existe',
                },
            )
        if edge.target not in by_id:
            errs.append(
                {
                    "field": f"edges[{ei}].target",
                    "message": f'no "{edge.target}" nao existe',
                },
            )

    if errs:
        return errs

    adj: dict[str, list[str]] = {}
    for edge in edges:
        adj.setdefault(edge.source, []).append(edge.target)

    WHITE, GREY, BLACK = 0, 1, 2
    state = {nid: WHITE for nid in by_id}

    def dfs_cycle(cur: str) -> bool:
        state[cur] = GREY
        for nei in adj.get(cur, ()):
            st = state.get(nei)
            if st == GREY:
                return True
            if st == WHITE:
                if dfs_cycle(nei):
                    return True
        state[cur] = BLACK
        return False

    if dfs_cycle(trigger_id):
        errs.append(
            {
                "field": "edges",
                "message": "o fluxo contem um ciclo (nao permitido)",
            }
        )
        return errs

    reachable = {trigger_id}
    stack = [trigger_id]
    while stack:
        u = stack.pop()
        for v in adj.get(u, ()):
            if v not in reachable:
                reachable.add(v)
                stack.append(v)

    unreachable = sorted(set(by_id) - reachable)
    if unreachable:
        for nid in unreachable:
            errs.append(
                {
                    "field": f"nodes.{nid}",
                    "message": "no nao alcancavel a partir do trigger",
                },
            )
        return errs

    has_action = False
    for nid in reachable:
        if by_id[nid].kind == "action":
            has_action = True
            break

    if not has_action:
        errs.append(
            {
                "field": "nodes",
                "message": (
                    "pelo menos um no action deve ser alcancavel a partir do trigger"
                ),
            },
        )

    return errs


def validate_flow_definition(raw: dict) -> list[dict[str, str]]:
    """Parse + regras; lista vazia se valido."""
    graph, coerce_err = coerce_flow_definition(raw)
    if coerce_err:
        return coerce_err
    assert graph is not None
    return validate_flow_structure(graph)

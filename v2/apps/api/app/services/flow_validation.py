"""Validacao estrutural de grafos de fluxo (Story 5.1)."""

from __future__ import annotations

from collections import deque
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

MAX_FLOW_NODES = 200


def _is_update_preferences_action(n: FlowNodePayload) -> bool:
    return n.kind == "action" and n.action_type == "update_preferences"


def _is_marketing_send_text(n: FlowNodePayload) -> bool:
    return (
        n.kind == "action"
        and n.action_type == "send_text"
        and n.preference_kind == "marketing"
    )


def _marketing_send_reachable_without_update_prefs(
    adj: dict[str, list[str]],
    by_id: dict[str, FlowNodePayload],
    trigger_id: str,
    target_id: str,
) -> bool:
    """True se existe caminho trigger -> target sem passar por update_preferences."""
    q: deque[tuple[str, bool]] = deque([(trigger_id, False)])
    seen: set[tuple[str, bool]] = set()
    while q:
        u, pe = q.popleft()
        if (u, pe) in seen:
            continue
        seen.add((u, pe))
        if u == target_id and _is_marketing_send_text(by_id[u]) and not pe:
            return True
        u_is = _is_update_preferences_action(by_id[u])
        for v in adj.get(u, ()):
            q.append((v, pe or u_is))
    return False


class FlowNodePayload(BaseModel):
    """Um no rule-based (trigger|condition|acao).

    Campos `action_*` aplicam-se quando ``kind == \"action\"`` (Story 5.5).
    """

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=128)
    kind: str = Field(
        ...,
        examples=["trigger", "condition", "action"],
    )
    action_type: str | None = Field(
        default=None,
        description=(
            'Para kind=action: "send_text" | "apply_tag" | "handoff" | '
            '"update_preferences".'
        ),
    )
    text_body: str | None = Field(default=None, max_length=4096)
    tag_name: str | None = Field(default=None, max_length=128)
    handoff_intent: str | None = Field(default=None, max_length=512)
    preference_kind: Literal["none", "marketing", "transactional"] | None = Field(
        default=None,
        description=(
            "Apenas em send_text: categoria outbound (omitido: transactional). "
            "`none` desliga o gate de preferencias no motor "
            "(como POST /messages/send; FR33)."
        ),
    )
    marketing_opt_in: bool | None = Field(
        default=None,
        description="Apenas em update_preferences: novo valor de opt-in marketing.",
    )
    transactional_allowed: bool | None = Field(
        default=None,
        description="Apenas em update_preferences: permite envios transacionais.",
    )
    disclosure_copy_slug: str | None = Field(default=None, max_length=128)

    @field_validator("kind")
    @classmethod
    def _kind_ok(cls, v: str) -> str:
        if v not in ("trigger", "condition", "action"):
            msg = 'kind deve ser trigger, condition ou action (recebido "{}")'
            raise ValueError(msg.format(v))
        return v

    @model_validator(mode="after")
    def _preference_fields_match_action(self):  # noqa: ANN201
        at = self.action_type
        slug = (self.disclosure_copy_slug or "").strip()
        has_pref_patch = (
            self.marketing_opt_in is not None
            or self.transactional_allowed is not None
            or bool(slug)
        )
        if self.preference_kind is not None and at != "send_text":
            raise ValueError(
                'preference_kind so e permitido quando action_type == "send_text"',
            )
        if has_pref_patch and at != "update_preferences":
            raise ValueError(
                "marketing_opt_in, transactional_allowed e disclosure_copy_slug "
                'apenas com action_type == "update_preferences"',
            )
        if at == "update_preferences" and self.preference_kind is not None:
            raise ValueError("update_preferences nao utiliza preference_kind")
        return self

    @field_validator("action_type")
    @classmethod
    def _action_type_ok(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if v not in ("send_text", "apply_tag", "handoff", "update_preferences"):
            msg = (
                "action_type deve ser send_text, apply_tag, handoff ou "
                'update_preferences (recebido "{}")'
            )
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

    for nid in reachable:
        n = by_id[nid]
        if n.kind != "action" or not n.action_type:
            continue
        if n.action_type == "send_text":
            if not (n.text_body and str(n.text_body).strip()):
                errs.append(
                    {
                        "field": f"nodes.{nid}.text_body",
                        "message": "obrigatorio quando action_type=send_text",
                    },
                )
        elif n.action_type == "apply_tag":
            if not (n.tag_name and str(n.tag_name).strip()):
                errs.append(
                    {
                        "field": f"nodes.{nid}.tag_name",
                        "message": "obrigatorio quando action_type=apply_tag",
                    },
                )
        elif n.action_type == "update_preferences":
            has_any = (
                n.marketing_opt_in is not None
                or n.transactional_allowed is not None
                or bool((n.disclosure_copy_slug or "").strip())
            )
            if not has_any:
                errs.append(
                    {
                        "field": f"nodes.{nid}",
                        "message": (
                            "update_preferences exige pelo menos um de: "
                            "marketing_opt_in, transactional_allowed, "
                            "disclosure_copy_slug"
                        ),
                    },
                )

    if errs:
        return errs

    for nid in reachable:
        if not _is_marketing_send_text(by_id[nid]):
            continue
        if _marketing_send_reachable_without_update_prefs(adj, by_id, trigger_id, nid):
            errs.append(
                {
                    "field": f"nodes.{nid}",
                    "message": (
                        "send_text com preference_kind=marketing exige que todo o "
                        "caminho desde o trigger passe por um no "
                        "update_preferences antes deste envio (Story 6.3)"
                    ),
                },
            )

    if errs:
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

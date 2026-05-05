"""Politica publica de ciclo de vida e deprecacao (Story 7.2 / FR37)."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

from app.core.publication import api_semantic_version

router = APIRouter(tags=["policy"])

REST_STABLE_PREFIX = "/v1"
# Janela documental minima antes de remocao (integradores: validar neste endpoint).
DEFAULT_COEXISTENCE_DAYS = 180


class DeprecationEntry(BaseModel):
    """Entrada futura: hoje a lista pode estar vazia (nenhum endpoint em sunset)."""

    model_config = ConfigDict(extra="forbid")

    method: str = Field(description="Metodo HTTP (ex.: GET, POST).")
    path: str = Field(description="Padrao de path sob o prefixo estavel `/v1`.")
    deprecated_since_date: str | None = Field(
        default=None,
        description=(
            "Data ISO8601 em que o recurso foi marcado deprecated (se aplicavel)."
        ),
    )
    sunset_date: str | None = Field(
        default=None,
        description=(
            "Data ISO8601 apos a qual o recurso pode ser removido "
            "(aviso juridico/operativo)."
        ),
    )
    replacement_hint: str | None = Field(
        default=None,
        description="Sugestao de migracao ou path substituto, se existir.",
    )


class DeprecationPolicyResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_semantic_version: str = Field(
        description="Versao semantica alinhada a OpenAPI info.version e ao CHANGELOG."
    )
    rest_stable_prefix: str = Field(
        default=REST_STABLE_PREFIX,
        description="Prefixo de contrato estavel atual (FR35).",
    )
    policy_summary: str = Field(
        description="Resumo da politica para integradores, em portugues."
    )
    deprecation_http_headers: str = Field(
        description=(
            "Como interpretar cabecalhos padrao Deprecation, Sunset e Link quando "
            "alguma rota entrar em fase de descontinuacao."
        ),
    )
    coexistence_window_days_guideline: int = Field(
        default=DEFAULT_COEXISTENCE_DAYS,
        description=(
            "Dias minimos recomendados de coexistencia antes de remover "
            "comportamento legacy."
        ),
    )
    changelog_reference: str = Field(
        description=("Referencia ao ficheiro de mudancas no repositorio (pacote API)."),
    )
    openapi_url_path: str = Field(
        default="/openapi.json",
        description="Path do documento OpenAPI desta instancia.",
    )
    deprecation_entries: list[DeprecationEntry] = Field(
        default_factory=list,
        description=(
            "Lista cronologica de recursos deprecated; vazia se nenhum esta anunciado."
        ),
    )


def _policy_body() -> DeprecationPolicyResponse:
    ver = api_semantic_version()
    return DeprecationPolicyResponse(
        api_semantic_version=ver,
        rest_stable_prefix=REST_STABLE_PREFIX,
        policy_summary=(
            "Versao atual do pacto REST: prefixo `/v1`. "
            "Mudancas incompativeis serao anunciadas aqui (`deprecation_entries`), "
            "no CHANGELOG da API e com cabecalhos HTTP nas rotas afetas "
            "(Deprecation, Sunset, Link). Mantenha consumo idempotente e "
            "respeite `Retry-After` em limites conforme Story 7.1."
        ),
        deprecation_http_headers=(
            "Quando um endpoint for descontinuado, a resposta pode incluir "
            "`Deprecation: true` e `Sunset` com data HTTP; use tambem esta "
            "rota GET para visao consolidada antes de remover clientes legacy."
        ),
        coexistence_window_days_guideline=DEFAULT_COEXISTENCE_DAYS,
        changelog_reference="CHANGELOG.md na raiz de `v2/apps/api/` (fonte)",
        deprecation_entries=[],
    )


@router.get(
    "/policy/deprecation",
    response_model=DeprecationPolicyResponse,
    summary="Politica publica de deprecacao e ciclo de vida (FR37)",
    description=(
        "Sem autenticacao. Lista janelas, cabecalhos esperados e entradas "
        "de rotas deprecated (quando existirem)."
    ),
)
def get_public_deprecation_policy() -> DeprecationPolicyResponse:
    return _policy_body()

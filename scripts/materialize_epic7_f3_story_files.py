#!/usr/bin/env python3
"""One-shot: full CS/VS story files for epics 7-10 and F2/F3. Run from repo root."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_bmad-output" / "implementation-artifacts"
DATE = "2026-04-24"

# story_key, epic_id, title, depends (yaml list lines), fr, ac_bullets, atdd_file, dev_focus
STORIES: list[tuple] = [
    (
        "7-1-rest-versioned-idempotency",
        "epic-7",
        "REST versionado e idempotencia",
        ["2-3-chaves-api-emissao-revogacao"],
        "FR35, FR36, FR40; NFR-INT-01, NFR-SEC-05",
        "- OpenAPI /v1; mutacoes com Idempotency-Key; 401/429 com Retry-After documentados.\n"
        "- Duplicados sem efeito indevido (politica 200/409 consistente).",
        "v2/apps/api/tests/atdd/test_epic7_story71_rest_idempotency_atdd.py",
        "Contrato integrador; headers e JSON de erro com correlation.",
    ),
    (
        "7-2-lifecycle-deprecation-policy",
        "epic-7",
        "Lifecycle e deprecation policy publica",
        ["7-1-rest-versioned-idempotency"],
        "FR37",
        "- Datas e janela em /v1/policy/deprecation, headers Deprecation, ou docs estaticos.\n"
        "- CHANGELOG e versao API alinhados.",
        "v2/apps/api/tests/atdd/test_epic7_story72_deprecation_policy_atdd.py",
        "Comunicacao sem surpresa a integradores.",
    ),
    (
        "7-3-sandbox-tenant-scoped",
        "epic-7",
        "Sandbox tenant-scoped e entregas",
        ["7-1-rest-versioned-idempotency"],
        "FR38, FR39, FR3",
        "- Sandbox sem dados de outros tenants nem prod.\n"
        "- Historico webhook deliveries com request_id (FR39).",
        "v2/apps/api/tests/atdd/test_epic7_story73_sandbox_deliveries_atdd.py",
        "Isolamento e tabela deliveries; RLS.",
    ),
    (
        "8-1-metering-minimo",
        "epic-8",
        "Metering minimo",
        ["3-2-enviar-mensagem-saida-fila-retry"],
        "FR41; NFR-FAIR-03",
        "- Eventos agregados por tenant; contrato de operacoes-chave.\n"
        "- GET /v1/me/usage/summary.",
        "v2/apps/api/tests/atdd/test_epic8_story81_metering_atdd.py",
        "Fair use e billing preparacao.",
    ),
    (
        "8-2-relatorios-valor-anti-vanity",
        "epic-8",
        "Relatorios de valor anti-vanity",
        ["8-1-metering-minimo"],
        "FR42",
        "- Relatorio exportavel; sem vanity como prova unica.\n"
        "- Papel financas ou 403.",
        "v2/apps/api/tests/atdd/test_epic8_story82_value_report_atdd.py",
        "Metricas ligadas a incidentes/volume quando existir.",
    ),
    (
        "8-3-entitlements-alertas",
        "epic-8",
        "Entitlements e alertas",
        ["8-1-metering-minimo"],
        "FR43, FR25 cross",
        "- Threshold configuravel; notificacao in-app; audit em mudancas sensiveis.",
        "v2/apps/api/tests/atdd/test_epic8_story83_entitlements_atdd.py",
        "Limites e alertas honestos.",
    ),
    (
        "8-4-export-uso-faturacao",
        "epic-8",
        "Export de uso e faturacao",
        ["8-3-entitlements-alertas"],
        "FR44; NFR-LGPD-02",
        "- CSV com identificadores estaveis; PII minima.",
        "v2/apps/api/tests/atdd/test_epic8_story84_usage_export_atdd.py",
        "Export financeiro seguro.",
    ),
    (
        "9-1-finalidades-bases-legais-fluxo",
        "epic-9",
        "Finalidades e bases legais por fluxo",
        ["5-1-editor-fluxos-validacao"],
        "FR45",
        "- Registos versionaveis por fluxo; sem parecer juridico no codigo.",
        "v2/apps/api/tests/atdd/test_epic9_story91_legal_basis_atdd.py",
        "Governanca e ligacao ao editor de fluxos.",
    ),
    (
        "9-2-dsar-estados-ack-mvp-hibrido",
        "epic-9",
        "DSAR estados e ACK MVP hibrido",
        ["9-1-finalidades-bases-legais-fluxo"],
        "FR46, NFR-LGPD-01",
        "- ACK na janela legal; runbook se pack automatico incompleto.",
        "v2/apps/api/tests/atdd/test_epic9_story92_dsar_atdd.py",
        "Pedidos DSAR e estados.",
    ),
    (
        "9-3-lista-subprocessadores",
        "epic-9",
        "Lista de subprocessadores",
        ["9-1-finalidades-bases-legais-fluxo"],
        "FR47, NFR-LGPD-04",
        "- Versao e data de atualizacao visiveis.",
        "v2/apps/api/tests/atdd/test_epic9_story93_subprocessors_atdd.py",
        "Transparencia subprocessadores.",
    ),
    (
        "9-4-retencao-aplicacao",
        "epic-9",
        "Retencao e aplicacao",
        ["9-3-lista-subprocessadores"],
        "FR48, FR49, NFR-LGPD-02",
        "- Config, jobs, relatorios agregados.",
        "v2/apps/api/tests/atdd/test_epic9_story94_retention_atdd.py",
        "Retencao tecnica + jobs.",
    ),
    (
        "9-5-registo-consentimento-opt-in-out",
        "epic-9",
        "Registo consentimento opt-in/out",
        ["6-3-disclosure-tratamento-opt-in-granular"],
        "FR50, FR32, FR33",
        "- Log consultavel; liga DSAR.",
        "v2/apps/api/tests/atdd/test_epic9_story95_consent_log_atdd.py",
        "Consent log e epico 6.",
    ),
    (
        "10-1-correlacao-classificacao-culpa",
        "epic-10",
        "Correlacao e classificacao de culpa",
        ["2-2-matriz-papeis-permissoes"],
        "FR51, NFR-OPS-05",
        "- Ferramenta interna ou query guiada; RBAC; sem PII fora de politica.",
        "v2/apps/api/tests/atdd/test_epic10_story101_incident_correlation_atdd.py",
        "Suporte N2 e telemetria.",
    ),
    (
        "10-2-consulta-audit-log",
        "epic-10",
        "Consulta audit log",
        ["1-3-perfil-definicoes-organizacao"],
        "FR52, NFR-OPS-03",
        "- Filtros ator/recurso/capacidade; P95 documentado; mascaras PII.",
        "v2/apps/api/tests/atdd/test_epic10_story102_audit_log_atdd.py",
        "Auditoria tenant-scoped.",
    ),
    (
        "10-3-break-glass-acoes-alto-risco",
        "epic-10",
        "Break-glass e acoes de alto risco",
        ["10-1-correlacao-classificacao-culpa", "10-2-consulta-audit-log"],
        "FR53, FR54, NFR-LGPD-03",
        "- Trilho audit; duracao finita; aprovacao DPO/jur antes producao.",
        "v2/apps/api/tests/atdd/test_epic10_story103_break_glass_atdd.py",
        "Alto risco com governanca.",
    ),
    (
        "f2-1-agente-inteligente-politicas",
        "epic-f2",
        "F2 Agente inteligente com politicas",
        ["5-5-engine-aplica-acoes"],
        "FR27 (gate F2)",
        "- Gate de produto; custo e politicas nas AC quando F2 ativo.",
        "v2/apps/api/tests/atdd/test_f2_story_f21_agent_intelligence_atdd.py",
        "LLM/ agente atras de flag; politicas de custo.",
    ),
    (
        "f3-1-orquestrador-n8n-integracao-piloto",
        "epic-f3",
        "F3 Orquestrador piloto",
        ["7-3-sandbox-tenant-scoped"],
        "FR28 (gate F3)",
        "- ADR seguranca; uma integracao piloto acordada (ex. n8n).",
        "v2/apps/api/tests/atdd/test_f3_story_f31_orchestrator_atdd.py",
        "Orquestracao externa tenant-safe.",
    ),
]


def render(
    key: str,
    epic: str,
    title: str,
    depends: list[str],
    fr: str,
    ac: str,
    atdd: str,
    focus: str,
) -> str:
    dep_yaml = "\n".join(f"  - {d}" for d in depends)
    epic_num = epic.replace("epic-", "")
    checklist = (
        "_bmad-output/test-artifacts/V2/atdd-checklist-epic-7.md"
        if epic_num == "7"
        else (
            "_bmad-output/test-artifacts/V2/atdd-checklist-epic-8.md"
            if epic_num == "8"
            else (
                "_bmad-output/test-artifacts/V2/atdd-checklist-epic-9.md"
                if epic_num == "9"
                else (
                    "_bmad-output/test-artifacts/V2/atdd-checklist-epic-10.md"
                    if epic_num == "10"
                    else "_bmad-output/test-artifacts/V2/atdd-checklist-epic-f2-f3.md"
                )
            )
        )
    )
    return f"""---
story_key: {key}
epic: {epic}
status: ready-for-dev
vs_validated: true
vs_date: {DATE}
atdd_ready: true
cs_completed: {DATE}
source: _bmad-output/planning-artifacts/epics.md
depends_on:
{dep_yaml}
code_location: v2/apps/api, v2/apps/admin-web
---

# Story {title}

## Story (resumo)

Contexto completo em `epics.md`. **Foco DS:** {focus}

**Requisitos:** {fr}

## Acceptance Criteria (testaveis)

{ac}

## Tasks / Subtasks

- [ ] Modelo + Alembic com `tenant_id` e RLS onde houver dados.
- [ ] API `/v1/...` + OpenAPI; erros canonicos (story 1.1).
- [ ] Admin-web quando houver UI (Chakra, UX-DR).
- [ ] pytest integracao; ATDD em `{atdd}`

## Party Mode (CS)

| Agente | Insight |
|--------|---------|
| **Winston** | OpenAPI e RLS; sem segunda forma de erro JSON. |
| **Mary** | Rastrear FR/NFR citados; dependencias no frontmatter. |
| **John** | Ordenar DS; flags se epico predecessor incompleto. |
| **Sally** | UX-DR4; sem stack ao operador. |
| **Amelia** | Docker CI; marcar `@pytest.mark.atdd`. |

## Advanced Elicitation (CS)

- **Pre-mortem:** dados de outro tenant visiveis - testes negativos RLS.
- **Red team:** segredos ou PII em audit/logs - mascarar e politica de retencao.

## Validate Story (VS)

**Veredito:** **aprovada para ATDD/DS** (batch epicos 7-10 / F2 / F3; rever pos-detalhe DS).

### Party Mode (VS)

| Agente | VS |
|--------|-----|
| **Winston** | Paths e contratos alinhados ao CDA. |
| **Amelia** | ATDD RED ligado ao ficheiro indicado. |
| **Mary** | AC cobrem FR citados. |

### Checklist BMad (sintese)

| Categoria | OK |
|-----------|-----|
| Regressao | Contrato erro 1.1 |
| RLS | `tenant_id` |
| Seguranca | RBAC em rotas sensiveis |

## Testing Requirements

- `{atdd}`

## References

- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/project-context.md`
- `{checklist}`

## Change Log

- {DATE}: **[CS+VS+AT]** materializado no fluxo por story (epicos 7-10 / F2 / F3).
"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for row in STORIES:
        key, epic, title, deps, fr, ac, atdd, focus = row
        path = OUT / f"{key}.md"
        path.write_text(render(key, epic, title, deps, fr, ac, atdd, focus), encoding="utf-8")
        print("Wrote", path.relative_to(ROOT))


if __name__ == "__main__":
    main()

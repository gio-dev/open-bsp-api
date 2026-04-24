---
title: ATDD Checklist - Epic 4
project: open-bsp-api
date: 2026-04-23
workflow: bmad-testarch-atdd
---

# ATDD Epic 4 - fase vermelha (por story)

## Resumo

Modulo pytest **por story** (4.1 -> 4.4), apos CS e VS. Execucao: Docker em `v2/`.

## API - ficheiros

| Story | Ficheiro |
|-------|----------|
| 4.1 | `v2/apps/api/tests/atdd/test_epic4_story41_inbox_split_atdd.py` |
| 4.2 | `v2/apps/api/tests/atdd/test_epic4_story42_etiquetas_atdd.py` |
| 4.3 | `v2/apps/api/tests/atdd/test_epic4_story43_handoff_atdd.py` |
| 4.4 | `v2/apps/api/tests/atdd/test_epic4_story44_channel_health_atdd.py` |

Marcador: `@pytest.mark.atdd`.

Paths sao **proposta RED**; ajustar ao OpenAPI no DS se o CDA fixar outros paths.

## Ordem GREEN sugerida

1. **4.1** - lista + thread (mensagens) + cabecalho no contrato; admin-web TanStack Query.
2. **4.2** - PATCH tags; RLS por tenant.
3. **4.3** - GET handoff + fila/roteamento API.
4. **4.4** - GET channel-health; banner/badge dados para UI.

## Stories

- `_bmad-output/implementation-artifacts/4-1-inbox-split-lista-thread.md`
- `_bmad-output/implementation-artifacts/4-2-etiquetas-triagem-partilhada.md`
- `_bmad-output/implementation-artifacts/4-3-handoff-contexto-minimo.md`
- `_bmad-output/implementation-artifacts/4-4-sinais-atraso-falha-health.md`

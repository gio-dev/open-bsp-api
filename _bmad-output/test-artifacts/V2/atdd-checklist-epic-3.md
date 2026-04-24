---
title: ATDD Checklist - Epic 3
project: open-bsp-api
date: 2026-04-23
workflow: bmad-testarch-atdd
---

# ATDD Epic 3 - fase vermelha (por story)

## Resumo

Modulo pytest **por story** (3.1 -> 3.3), apos CS e VS de cada uma. Execucao: Docker em `v2/`.

## API - ficheiros

| Story | Ficheiro |
|-------|----------|
| 3.1 | `v2/apps/api/tests/atdd/test_epic3_story31_webhook_ingress_atdd.py` |
| 3.2 | `v2/apps/api/tests/atdd/test_epic3_story32_send_message_atdd.py` |
| 3.3 | `v2/apps/api/tests/atdd/test_epic3_story33_templates_signals_atdd.py` |

Marcador: `@pytest.mark.atdd`.

## Ordem GREEN sugerida

1. **3.1** - GET verificacao Meta + POST ingress + fila com tenant resolvido.
2. **3.2** - POST send + estados + 429/Retry-After quando aplicavel.
3. **3.3** - GET templates + sinais; UI admin opcional neste repo.

## Stories

- `_bmad-output/implementation-artifacts/3-1-webhook-entrada-verificacao-encaminhamento.md`
- `_bmad-output/implementation-artifacts/3-2-enviar-mensagem-saida-fila-retry.md`
- `_bmad-output/implementation-artifacts/3-3-templates-sinais-opt-in-qualidade.md`

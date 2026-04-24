---
title: ATDD Checklist - Epic 6
project: open-bsp-api
date: 2026-04-24
workflow: bmad-testarch-atdd
---

# ATDD Epic 6 - fase vermelha (por story)

## API (+ embed)

| Story | Ficheiro |
|-------|----------|
| 6.1 | `v2/apps/api/tests/atdd/test_epic6_story61_embed_session_atdd.py` |
| 6.2 | `v2/apps/api/tests/atdd/test_epic6_story62_bot_human_mode_atdd.py` |
| 6.3 | `v2/apps/api/tests/atdd/test_epic6_story63_disclosure_preferences_atdd.py` |
| 6.4 | `v2/apps/api/tests/atdd/test_epic6_story64_embed_a11y_atdd.py` |

Marcador: `@pytest.mark.atdd`. **6.4** aceita 200 ou 404 ate existir endpoint de metadados a11y.

## Ordem GREEN sugerida

6.1 sessao embed -> 6.2 modo conversa -> 6.3 preferencias -> 6.4 a11y embed + auditoria UX.

## Stories

- `_bmad-output/implementation-artifacts/6-1-embed-autenticado-jwt-validacao-origem.md`
- `_bmad-output/implementation-artifacts/6-2-copy-estados-bot-humano.md`
- `_bmad-output/implementation-artifacts/6-3-disclosure-tratamento-opt-in-granular.md`
- `_bmad-output/implementation-artifacts/6-4-acessibilidade-embed.md`

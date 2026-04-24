---
title: ATDD Checklist - Epic 5
project: open-bsp-api
date: 2026-04-23
workflow: bmad-testarch-atdd
---

# ATDD Epic 5 - fase vermelha (por story)

## API - ficheiros

| Story | Ficheiro |
|-------|----------|
| 5.1 | `v2/apps/api/tests/atdd/test_epic5_story51_flow_editor_atdd.py` |
| 5.2 | `v2/apps/api/tests/atdd/test_epic5_story52_sandbox_atdd.py` |
| 5.3 | `v2/apps/api/tests/atdd/test_epic5_story53_publish_atdd.py` |
| 5.4 | `v2/apps/api/tests/atdd/test_epic5_story54_versions_audit_atdd.py` |
| 5.5 | `v2/apps/api/tests/atdd/test_epic5_story55_engine_atdd.py` |

Marcador: `@pytest.mark.atdd`. Paths sao **proposta RED**; alinhar ao OpenAPI no DS.

## Ordem GREEN sugerida

5.1 validacao -> 5.2 sandbox -> 5.3 publish -> 5.4 versoes -> 5.5 engine (com 3.1 + 5.3).

## Stories

- `_bmad-output/implementation-artifacts/5-1-editor-fluxos-validacao.md`
- `_bmad-output/implementation-artifacts/5-2-sandbox-preview.md`
- `_bmad-output/implementation-artifacts/5-3-publish-permissao-ambiente.md`
- `_bmad-output/implementation-artifacts/5-4-versao-audit-materialidade.md`
- `_bmad-output/implementation-artifacts/5-5-engine-aplica-acoes.md`

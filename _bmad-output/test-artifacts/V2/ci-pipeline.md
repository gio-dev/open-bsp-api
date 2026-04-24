---
title: CI pipeline (BMad testarch-ci) ? v2
execution: Docker apenas
workflow: .github/workflows/ci-v2-docker.yml
updated: 2026-04-23
---

# Pipeline de qualidade v2

## Objetivo

Garantir **Ruff + pytest** (API) e **ESLint + Vitest + build** (admin) **só via Docker**, com **política OpenAPI** automatizada e **ATDD** incluído no mesmo gate de merge.

## Regra ATDD e merge

| Estado | Comportamento no CI |
| ------ | --------------------- |
| Teste ATDD **vermelho** (falha) | Job falha ? **merge bloqueado** para `main` / `develop` |
| Teste ATDD **verde** | Job passa ? merge permitido (resto dos gates OK) |

Os testes ATDD vivem em:

- API: `v2/apps/api/tests/atdd/` (`@pytest.mark.atdd`)
- Admin: `v2/apps/admin-web/src/atdd/` (`*.test.tsx`, etc.)

Checklist Epic 1 (RED): `_bmad-output/test-artifacts/V2/atdd-checklist-epic-1.md`.

## Gates por componente

| Gate | Onde corre | Comando (resumo) |
| ---- | ---------- | ------------------ |
| Lint + formato API | `api-ci` | `ruff check . && ruff format --check .` |
| Testes API (unit, smoke, **policy**, **atdd**) | `api-ci` | `pytest -q` |
| OpenAPI (política) | `api-ci` | `pytest` recolhe `tests/policy/` (marcador `policy`) |
| Lint admin | `admin-web-ci` | `npm run lint` |
| Testes admin (incl. **atdd** quando existirem) | `admin-web-ci` | `npm run test -- --run` |
| Build admin | `admin-web-ci` | `npm run build` |

## Política OpenAPI

Automatizada em `v2/apps/api/tests/policy/test_openapi_gate.py` (marcador `policy`):

- OpenAPI **3.x**
- `info.title` e `info.version` presentes
- Paths `/v1/health` e `/v1/ready` com `GET` documentados
- Resposta `/openapi.json` é JSON objeto (`application/json`)

Evoluções (Spectral, diff vs baseline, etc.) podem acrescentar-se aqui ou em job dedicado; até lá, estes checks são o **mínimo** no pipeline.

## Ficheiros relacionados

- `v2/README.md` ? comandos Docker locais
- `_bmad-output/test-artifacts/V2/test-framework.md` ? pastas e smoke
- `_bmad-output/test-artifacts/V2/test-design/open-bsp-api-handoff.md` ? sequência BMad

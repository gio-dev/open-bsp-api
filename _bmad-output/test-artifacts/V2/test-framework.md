---
title: Test Framework (TF) ? open-bsp-api v2
version: V2
stack: pytest (API) + Vitest (admin-web)
execution: Docker apenas (v2/README.md)
updated: 2026-04-23
---

# Test Framework ? convenções

## Execução canónica

Sempre a partir de **`v2/`**, via `docker compose --profile ci` (ver `v2/README.md`). Não é obrigatório `venv` nem `npm install` no host.

| Suite | Comando (dentro do container CI) | Docker (exemplo) |
| ----- | -------------------------------- | ---------------- |
| API ? completa | `ruff check . && ruff format --check . && pytest -q` | `docker compose --profile ci run --rm api-ci` |
| API ? smoke | `pytest -q -m smoke` (+ Ruff se quiser gate igual à CI) | ver `v2/README.md` |
| Admin ? completa | `npm run lint && npm run test -- --run && npm run build` | `docker compose --profile ci run --rm --no-deps admin-web-ci` |
| Admin ? smoke | `npm run test:smoke` | `docker compose --profile ci run --rm --no-deps admin-web-ci sh -c "npm run test:smoke"` |

## API (pytest)

| Item | Convenção |
| ---- | --------- |
| Raiz | `v2/apps/api/tests/` |
| Ficheiros | `test_*.py` |
| Classes de teste | `Test*` (quando usadas) |
| Funções | `test_*` |
| Smoke | Marcador `@pytest.mark.smoke` + módulos em **`tests/smoke/`** (subconjunto mínimo pós-deploy) |
| Fixtures partilhadas | `tests/conftest.py` |
| Config | `[tool.pytest.ini_options]` em `pyproject.toml` |

Marcadores registados em `pyproject.toml` (evita avisos Pytest 8+).

## Admin-web (Vitest + Testing Library)

| Item | Convenção |
| ---- | --------- |
| Colocação | Por defeito **colocalizado**: `*.test.ts` / `*.test.tsx` junto ao código (ex.: `App.test.tsx`) |
| Smoke | Ficheiros em **`src/smoke/`**, sufixo `*.test.tsx` (suite mínima de shell) |
| Config | `vite.config.ts` ? `test.environment: "jsdom"`, `setupFiles: "./src/setupTests.ts"` |
| Comando suite completa | `npm run test` / `vitest` |
| Comando smoke | `npm run test:smoke` (`vitest run src/smoke`) |

## Níveis (evolução)

- **Smoke:** liveness da API + render mínimo do admin (sem E2E browser).
- **Unit / contract:** testes atuais de health, OpenAPI, erros canónicos; componentes React.
- **E2E (futuro):** Playwright/Cypress quando o handoff ATDD o exigir; `data-testid` estável em fluxos P0.

## Ligação ao handoff BMad

Ver `_bmad-output/test-artifacts/V2/test-design/open-bsp-api-handoff.md` (sequência TD ? TF ? CI ? ?).

**CI / ATDD / OpenAPI:** `_bmad-output/test-artifacts/V2/ci-pipeline.md`.

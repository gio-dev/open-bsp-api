---
workflowType: testarch-test-design
document: qa
version: V2
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/epics.md
  - _bmad-output/planning-artifacts/nfr-story-coverage-matrix.md
  - _bmad-output/test-artifacts/V2/test-design-architecture.md
---

# Test design (QA): open-bsp-api - V2

**Proposito:** receita de execucao: o que testar, nivel, ferramentas (alinhado CDA).

**Data:** 2026-04-23  
**Autor:** TEA  
**Estado:** Rascunho  
**Relacionado:** `V2/test-design-architecture.md`

---

## Resumo

**Ambito:** FR1-FR54 (exceto FR27/28 fora nucleo MVP), NFRs PRD, UX-DR1-DR10 aplicavel.

**Riscos:** 14; 6 com score >= 6. Categorias criticas: SEC, DATA, BUS, PERF.

**Cobertura indicativa (P0-P3 = prioridade/risco, nao timing de CI):**

| Pri | Qtd ref | Foco |
| --- | ------- | ---- |
| P0 | ~35-50 | RLS, webhooks, auth, idempotencia, erros canonicos |
| P1 | ~55-85 | Inbox, regras, sandbox, API publica, quotas, LGPD |
| P2 | ~40-70 | Relatorios, a11y embed, deprecation API |
| P3 | ~15-30 | Exploratorio, benchmarks, caos pos-MVP |
| Total | ~145-235 | |

---

## Fora de ambito MVP

| Item | Razao | Mitigacao |
| ---- | ----- | --------- |
| FR27/28 | Fase 2/3 | Testes quando f2/f3 no sprint |
| Chaos multi-regiao | Infra pesada | Semanal pos baseline |
| Carga pico extremo | Fora piloto | k6 noturno limites Anexo A |

---

## Dependencias

1. **B-01** seed/reset - Backend
2. **B-03** stubs Meta+fila - Backend
3. **B-02** OpenAPI CI - Platform

**Infra QA:** factories (Tenant, User+papel, WABA, mensagem minima, API key, webhook secret); Docker Postgres local/CI; staging NFR-SEC-01.

### Exemplo pytest (API)

```python
import pytest
from httpx import ASGITransport, AsyncClient

@pytest.fixture
async def api_client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_p0_unauthorized_canonical(api_client):
    r = await api_client.post("/v1/example", json={})
    assert r.status_code == 401
    body = r.json()
    assert "code" in body and "message" in body and "request_id" in body
```

### Exemplo Playwright (futuro admin-web)

```typescript
import { test, expect } from '@playwright/test';

test('@P0 @E2E smoke login', async ({ page }) => {
  await page.goto('/login');
  await expect(page.getByRole('heading', { name: /inbox|entrada/i })).toBeVisible({
    timeout: 15_000,
  });
});
```

---

## Riscos (visao QA)

### Altos

| ID | Cat | Scr | Cobertura |
| -- | --- | --- | ---------- |
| R-001 | SEC | 6 | Tenant A nunca ve dados B |
| R-002 | SEC | 6 | HMAC/replay/frescura -> 4xx |
| R-003 | DATA | 6 | Double POST idempotente estavel |
| R-004 | BUS | 6 | Estado honesto fila/429 |
| R-005 | PERF | 6 | Carga noturna staging |
| R-006 | SEC | 6 | JWT x Origin embed |

### Medios/baixos

R-007 a R-014: golden erro, backoff Meta, DSAR, a11y, copy, ambientes, PII - cruzar `nfr-story-coverage-matrix.md`.

---

## Criterios

**Entrada:** PRD/CDA/epicos aceites; B-01 a B-03 resolvidos ou waived; ambiente+factories; historia ready-for-dev com AC validados.

**Saida:** P0 100%; P1 >= 95% ou triaged aceite; sem bugs criticos P0; NFR baseline quando aplicavel.

---

## Plano de cobertura (amostra)

**P0:** FR3 RLS; FR11-13 webhooks; FR35 idempotencia; FR40 erros; FR5-7 auth; FR29 embed; health smoke.

**P1:** FR17-21 inbox; FR22-26 regras/motor; FR35-40 API; FR41-44 uso; FR45-50 LGPD.

**P2:** FR34 a11y; FR37 deprecation; FR39 debugger integrador.

**P3:** exploratorio manual; k6 spike.

---

## Estrategia de execucao

**PR (alvo < 15 min):** `ruff` + `pytest`; `eslint` + `vitest`; validacao OpenAPI quando existir.

**Noturno (30-60 min):** k6 rotas criticas; burn-in opcional.

**Semanal:** caos/degradacao Meta (NFR-OPS-02); E2E Playwright ampliado.

---

## Esforco (QA/automacao, intervalos)

| Pri | Ref | Semanas (1 FTE) |
| --- | --- | ----------------- |
| P0 | 35-50 | 4-8 |
| P1 | 55-85 | 8-14 |
| P2 | 40-70 | 6-12 |
| P3 | 15-30 | 1-3 |
| Total | 145-235 | 19-37 (paralelo dev/test ~9-18 pessoa) |

---

## Ferramentas

pytest+httpx; Vitest; Playwright (UI estavel); k6; Postgres Docker.

---

## Regressao

Alteracoes em API/OpenAPI, webhooks, Alembic/RLS: suite pytest completa em PR; Vitest admin; P0-002 em mudancas de borda webhook.

---

## Apendice - tags

`@P0` `@API` `@RLS` `@WH` `@AUTH` `@EMBED` `@LGPD`

**Workflow:** `bmad-testarch-test-design` V2

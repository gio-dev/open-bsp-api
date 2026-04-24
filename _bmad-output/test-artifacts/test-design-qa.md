---
workflowType: testarch-test-design
document: qa
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/epics.md
  - _bmad-output/planning-artifacts/nfr-story-coverage-matrix.md
  - _bmad-output/test-artifacts/test-design-architecture.md
---

# Test design (QA): open-bsp-api

**Propósito:** receita de execução de testes: o que testar, a que nível e com que ferramentas, alinhado ao CDA.

**Data:** 2026-04-23  
**Autor:** TEA (Master Test Architect)  
**Estado:** Rascunho  
**Projeto:** open-bsp-api  

**Relacionado:** `test-design-architecture.md` (testabilidade, bloqueadores, riscos ? 6).

---

## Resumo executivo

**Âmbito:** validação de FR1?FR54 (exceto FR27/FR28 fora do núcleo MVP), NFRs do inventário PRD, requisitos UX-DR1?DR10 onde aplicável.

**Riscos (sumário):** 14 riscos; **6** com score ? 6 (ver doc de arquitetura). Categorias mais críticas: **SEC**, **DATA**, **BUS**, **PERF**.

**Cobertura (ordenação P0?P3 = prioridade e risco, não calendário de execução):**

| Prioridade | Contagem indicativa | Foco |
|------------|---------------------|------|
| P0 | ~35?50 | RLS, webhooks, auth, idempotência, erros canónicos, isolamento tenant |
| P1 | ~55?85 | Inbox, regras, sandbox, API pública, quotas, LGPD operacional |
| P2 | ~40?70 | Relatórios, a11y embed, *edge* de versão API |
| P3 | ~15?30 | Exploratório, benchmarks, caos (pós-MVP) |
| **Total** | **~145?235** | Ver intervalos de esforço abaixo |

---

## Fora de âmbito (MVP)

| Item | Razão | Mitigação |
|------|--------|-----------|
| FR27 / FR28 (agente / orquestrador avançado) | Fase 2/3 | Testes quando histórias `f2-*` / `f3-*` entrarem no sprint |
| *Chaos* multi-região completo | Infraestrutura pesada | Semanal pós *baseline* de disponibilidade |
| Carga extrema tipo *peak* Black Friday | Fora piloto inicial | *Nightly* k6 com limites do Anexo A |

---

## Dependências e bloqueios

### Backend / arquitetura (pré-implementação)

1. **Seed / reset de dados (B-01)** ? Backend ? antes de ATDD em massa. Sem isto: paralelização fraca e *state leak* entre testes.
2. **Stubs Meta + fila (B-03)** ? Backend ? necessário para Épico 3 sem flakiness. Cobrir com *fakes* em memória ou *testcontainers* conforme decisão de arquitetura.
3. **Job OpenAPI em CI (B-02)** ? Platform ? bloqueia regressões de contrato que Vitest/admin assumem.

### Infraestrutura QA

1. **Factories** ? entidades: `Tenant`, `User`+papel, `WABA`, conversa/mensagem mínima, chave API, segredo webhook (dados sintéticos).
2. **Ambientes** ? local: Docker Postgres + API + variáveis de segredo de teste; CI: mesma imagem; *staging* alinhado a NFR-SEC-01.

### Exemplo API (pytest + cliente HTTP)

Padrão alvo do CDA (`httpx` / `TestClient` FastAPI):

```python
import pytest
from httpx import ASGITransport, AsyncClient

@pytest.fixture
async def api_client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_p0_unauthorized_returns_canonical_error(api_client):
    r = await api_client.post("/v1/example", json={})
    assert r.status_code == 401
    body = r.json()
    assert "code" in body and "message" in body
    assert "request_id" in body
```

### Exemplo E2E futuro (admin-web; Playwright)

Com `tea_use_playwright_utils: true`, quando existir `apps/admin-web`, usar utilitários de API + browser para jornadas P0 (login, inbox). *Snippet* ilustrativo:

```typescript
import { test, expect } from '@playwright/test';

test('@P0 @E2E login redirects to inbox smoke', async ({ page }) => {
  // placeholders: substituir por rotas reais após scaffold
  await page.goto('/login');
  await expect(page.getByRole('heading', { name: /inbox|caixa de entrada/i })).toBeVisible({
    timeout: 15_000,
  });
});
```

---

## Riscos (visão QA)

### Altos (? 6)

| Risk ID | Categoria | Descrição | Score | Cobertura QA |
| -------- | --------- | ----------- | ----- | ------------- |
| R-001 | SEC | *Cross-tenant* | 6 | Integração: credenciais tenant A nunca retornam dados B |
| R-002 | SEC | Webhook inválido | 6 | API: HMAC/replay/frescura ? 4xx documentados |
| R-003 | DATA | Idempotência | 6 | *Double POST* com mesma chave ? resultado estável |
| R-004 | BUS | Falso sucesso | 6 | Contrato de estado + UX: fila/429 visíveis |
| R-005 | PERF | SLO ingest/envio | 6 | *Nightly* carga *smoke* + alertas em *staging* |
| R-006 | SEC | Embed origem | 6 | API/UI: JWT + `Origin` negativo e positivo |

### Médios / baixos

| Risk ID | Score | Cobertura QA resumida |
| ------- | ----- | ---------------------- |
| R-007 | 4 | *Golden* JSON erro; header `request_id` |
| R-008 | 4 | Simulação 429 Meta; *retry* com *backoff* |
| R-009 | 4 | DSAR: transições e prazos |
| R-010?R-014 | ? 3 | A11y, copy, ambientes, dados ? ver matriz NFR?história |

---

## Critérios de entrada

- [ ] PRD, CDA e épicos aceites para o *incremento* em curso
- [ ] Bloqueadores B-01?B-03 resolvidos ou explicitamente *waived* com dono
- [ ] Ambiente de teste acessível; factories mínimas disponíveis
- [ ] *Feature* ou API deployada no alvo de teste
- [ ] História em `ready-for-dev` com AC validados (`bmad-create-story:validate`)

## Critérios de saída

- [ ] 100% dos testes P0 da *release* a passar
- [ ] P1 ? 95% ou falhas *triaged* aceites por QA + Dev Lead
- [ ] Sem defeitos abertos **críticos** nos fluxos P0
- [ ] Baselines de desempenho (quando NFR aplicável) dentro do orçamento acordado

---

## Plano de cobertura

**Nota:** P0/P1/P2/P3 indicam **prioridade e severidade de risco**, não «correr só P0 no CI». Ver **Estratégia de execução**.

### P0 (crítico)

| Test ID | Requisito | Nível | Risk | Notas |
| ------- | --------- | ----- | ---- | ----- |
| P0-001 | FR3 + RLS | Integração | R-001 | CRUD representativo por *tenant* |
| P0-002 | FR11?FR13 webhooks | Integração | R-002 | Válido / inválido / *replay* |
| P0-003 | FR35 idempotência | API | R-003 | Mutações com `Idempotency-Key` |
| P0-004 | FR40 erros | API | R-004, R-007 | 401/403/429 + corpo canónico |
| P0-005 | FR5?FR7 auth consola | Integração | R-001 | Papéis e negação |
| P0-006 | FR29 embed + origem | Integração/API | R-006 | Matriz JWT × Origin |
| P0-007 | Health + *smoke* monorepo | API | R-005 | *Smoke* pós-deploy |

**Total P0:** ~35?50 casos (inclui variantes negativas).

### P1 (alto)

| Test ID | Requisito | Nível | Risk | Notas |
| ------- | --------- | ----- | ---- | ----- |
| P1-001 | FR17?FR21 inbox/handoff | Integração / E2E | R-004 | Lista \| *thread* + sinais honestos |
| P1-002 | FR22?FR26 regras + motor | Integração | BUS | *Sandbox* vs *publish* |
| P1-003 | FR35?FR40 API pública | API | R-003 | Versionamento `/v1` |
| P1-004 | FR41?FR44 uso/quotas | API | NFR-FAIR | *Metering* mínimo |
| P1-005 | FR45?FR50 LGPD | API | R-009 | DSAR, retenção, consentimento |

**Total P1:** ~55?85 casos.

### P2 (médio)

| Test ID | Requisito | Nível | Notas |
| ------- | --------- | ----- | ----- |
| P2-001 | FR34 / NFR-A11Y | Componente / a11y | axe + teclado em *embed* |
| P2-002 | FR37 *deprecation* | API | Cabeçalhos / política documentada |
| P2-003 | FR39 *debugger* integrador | API | Histórico entregas *webhook* |

**Total P2:** ~40?70 casos.

### P3 (baixo)

| Test ID | Requisito | Nível | Notas |
| ------- | --------- | ----- | ----- |
| P3-001 | Exploratório UX | Manual | *Checklist* por release |
| P3-002 | Benchmarks | k6 | *Spike* acordado com SLO |

**Total P3:** ~15?30 casos.

---

## Estratégia de execução

**Filosofia:** tudo o que for **rápido e determinístico** corre em **PR**; o que for caro ou longo vai para **noturno** / **semanal**.

### Cada PR (alvo &lt; 15 min após paralelização)

- **API:** `ruff check` + `pytest` (unit + integração com BD de teste / *containers*).
- **Admin:** `eslint` + `vitest` (componentes, *hooks*).
- **Contrato:** diff ou validação de `openapi.json` quando o *job* existir (B-02).

### Noturno (~30?60 min)

- **k6** ou equivalente: rotas críticas (ingest, envio, auth) contra *staging* ou *mock* dedicado.
- *Burn-in* opcional de suíte lenta.

### Semanal

- Cenários de **caos** / degradação Meta (NFR-OPS-02) quando infra existir.
- Regressão E2E Playwright ampliada (jornadas consola + embed).

**Manual:** operações de *release*, validação financeira de relatórios, *sign-off* UAT por PM quando exigido.

---

## Estimativa de esforço (só QA / automação)

| Prioridade | Contagem indicativa | Esforço (1 FTE QA/automação) |
|------------|---------------------|------------------------------|
| P0 | ~35?50 | ~4?8 semanas |
| P1 | ~55?85 | ~8?14 semanas |
| P2 | ~40?70 | ~6?12 semanas |
| P3 | ~15?30 | ~1?3 semanas |
| **Total** | **~145?235** | **~19?37 semanas** (com paralelismo de dev/test cai para ~9?18 semanas·pessoa) |

**Pressupostos:** factories prontas; *stubs* Meta; não inclui *DevOps* de primeira configuração de *cluster*.

---

## Handoff de implementação (opcional)

| Work item | Owner | Notas |
| --------- | ----- | ----- |
| Scaffold pytest + *fixtures* Postgres | Dev | História 1-1 |
| Job OpenAPI CI | Platform | B-02 |
| *Fake* WhatsApp + fila | Dev | Épico 3 |
| Primeira onda ATDD P0 | QA + Dev | Após `bmad-testarch-atdd` |

---

## Ferramentas e acesso

| Ferramenta | Uso | Estado |
|------------|-----|--------|
| pytest + httpx | API / integração | Alvo CDA |
| Vitest + Testing Library | admin-web | Alvo CDA |
| Playwright | E2E consola/embed | Quando UI estável |
| k6 | Carga | *Staging* + credenciais |
| Postgres (Docker) | BD teste | Local + CI |

---

## Interoperabilidade e regressão

| Componente | Impacto | Regressão |
|------------|---------|-----------|
| `apps/api` | Contrato OpenAPI + RLS | *Suite* pytest completa em PR |
| `apps/admin-web` | Consumidor OpenAPI | Vitest + E2E *smoke* |
| Webhooks | Assinatura + *routing* | P0-002 em cada alteração de borda |
| Migração Alembic | RLS/políticas | Testes de isolamento obrigatórios |

**Estratégia:** antes de *release*, PR verde + *nightly* verde + amostra P1 relacionada com diff do PR.

---

## Apêndice A ? Etiquetas sugeridas

- `@P0` `@P1` ? prioridade de risco  
- `@API` `@RLS` `@WH` (webhook) `@AUTH` `@EMBED` `@LGPD`  

Execução por *grep* (pytest: `-k "p0"` ou *markers*; Playwright: `--grep @P0`).

## Apêndice B ? Referências da base de conhecimento TEA

- `risk-governance.md`, `probability-impact.md`, `test-levels-framework.md`, `test-priorities-matrix.md`, `test-quality.md`

---

**Gerado por:** BMad TEA ? workflow `bmad-testarch-test-design`  
**Versão:** 4.0 (BMad v6)

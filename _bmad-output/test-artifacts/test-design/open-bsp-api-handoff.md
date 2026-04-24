---
title: TEA Test Design ? BMAD Handoff
version: '1.0'
workflowType: testarch-test-design-handoff
sourceWorkflow: testarch-test-design
generatedBy: TEA Master Test Architect
generatedAt: '2026-04-23T12:00:00Z'
projectName: open-bsp-api
inputDocuments:
  - _bmad-output/test-artifacts/test-design-architecture.md
  - _bmad-output/test-artifacts/test-design-qa.md
  - _bmad-output/planning-artifacts/epics.md
  - _bmad-output/planning-artifacts/nfr-story-coverage-matrix.md
---

# TEA ? BMAD: handoff de qualidade (open-bsp-api)

## Propósito

Ligar o *test design* TEA ao fluxo BMAD (histórias, ATDD, implementação). Os épicos/histórias já existem em `epics.md`; este documento fixa **gates**, **riscos** e **cenários** que devem aparecer nos AC ou na suíte.

## Inventário de artefactos TEA

| Artefacto | Caminho | Ponto de integração BMAD |
| --------- | ------- | ------------------------ |
| Test design (arquitetura) | `_bmad-output/test-artifacts/test-design-architecture.md` | Bloqueadores B-01?B-03; riscos ?6; testabilidade |
| Test design (QA) | `_bmad-output/test-artifacts/test-design-qa.md` | Níveis, prioridades P0?P3, execução CI |
| Progresso workflow | `_bmad-output/test-artifacts/test-design-progress.md` | Auditoria do TD |
| Matriz NFR ? história | `_bmad-output/planning-artifacts/nfr-story-coverage-matrix.md` | Critérios de aceitação NFR por ID |

---

## Orientação ao nível de épico

### Referências de risco (gates)

- Nenhum épico que toque **dados de tenant** ou **webhooks** deve fechar sem mitigação **R-001** e **R-002** demonstrada em testes automatizados.
- Épico 7 (API pública) exige evidência **R-003** (idempotência) e **R-004/R-007** (erros canónicos).
- Épico 6 (embed) exige evidência **R-006** antes de *GA* do *embed*.

### Quality gates recomendados por épico

| Épico | Gate mínimo |
| ----- | ------------ |
| 1 | CI verde (lint + test) + prova RLS **1-2** |
| 2 | Matriz papéis + rotação segredos com testes de negação |
| 3 | Webhook: *happy* + inválido + *replay* |
| 4 | Inbox: estados honestos (UX-DR4) cobertos em integração/E2E |
| 5 | *Sandbox* ? *prod* + motor de regras determinístico |
| 6 | *Origin* + JWT embed |
| 7 | OpenAPI validado em PR + *double-submit* idempotente |
| 8?10 | Conforme `nfr-story-coverage-matrix.md` |

---

## Orientação ao nível de história (AC)

### Cenários P0 que devem constar dos AC (ou de testes ATDD ligados)

1. **Isolamento tenant:** utilizador/token do tenant A não acede a recursos do tenant B (API e, quando aplicável, UI).
2. **Webhook:** assinatura inválida ? 4xx documentado; *replay* detectado ? rejeição.
3. **Idempotência:** segunda mutação com a mesma `Idempotency-Key` não duplica efeito negócio.
4. **Erro canónico:** 401/403/429 retornam JSON com `code`, `message`, `request_id` (e `Retry-After` quando 429).
5. **Embed:** pedido com JWT válido e origem fora da *allowlist* ? negado.

### Testabilidade (atributos / contratos)

- Expor `data-testid` (ou equivalente estável) nos fluxos **P0** da consola quando Playwright for usado (inbox, login, *drawer* de regras).
- Manter exemplos `curl`/JSON no OpenAPI ou `docs/modular` para P1-003 (integrador).

---

## Mapeamento risco ? história (amostra)

| Risk ID | P×I | Histórias / épico (referência sprint) | Nível de teste |
| ------- | --- | -------------------------------------- | -------------- |
| R-001 | 6 | `1-2-modelo-tenant-rls-?`, épicos 2?10 com dados | Integração |
| R-002 | 6 | `3-1-webhook-entrada-?` | Integração |
| R-003 | 6 | `7-1-rest-versioned-idempotency`, `3-2-enviar-mensagem-?` | API |
| R-004 | 6 | `3-2-?`, `4-4-sinais-atraso-?` | API + UI |
| R-005 | 6 | `3-1-?`, `7-1-?`, NFR-PERF-* | Carga (*nightly*) |
| R-006 | 6 | `6-1-embed-autenticado-?` | API / E2E |
| R-007 | 4 | `1-1-monorepo-?`, todas as rotas públicas | API (*golden*) |
| R-009 | 4 | `9-2-dsar-?` | API |

*(Completar com `nfr-story-coverage-matrix.md` para NFRs restantes.)*

---

## Sequência BMAD ? TEA recomendada

1. **TD** (concluído) ? este handoff  
2. **TF** ? *framework* pytest/Vitest + estrutura de pastas  
3. **CI** ? Ruff, pytest, ESLint, Vitest, OpenAPI  
4. **CS / VS** ? história pronta  
5. **AT** ? testes de aceitação *red*  
6. **DS** ? implementação  
7. **CR** ? revisão incluindo flakiness  
8. **TA / TR** ? automação expandida e matriz de rasto  

## Gates de transição de fase

| De | Para | Critério |
| -- | ---- | -------- |
| Test design | Implementação | B-01?B-03 com dono; riscos ?6 com mitigação planeado |
| ATDD | Dev | Falha vermelha reprodutível para cada P0 da história |
| Dev | Release candidate | P0 100% verde; P1 conforme política do doc QA |

---

**Consumidores:** *refinement* de histórias, `bmad-testarch-atdd`, *owners* de épico.

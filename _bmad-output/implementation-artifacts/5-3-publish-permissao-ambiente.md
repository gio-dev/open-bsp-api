---
story_key: 5-3-publish-permissao-ambiente
epic: epic-5
status: ready-for-dev
vs_validated: true
vs_date: 2026-04-23
atdd_ready: true
cs_completed: 2026-04-23
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 5-2-sandbox-preview
code_location: v2/apps/api, v2/apps/admin-web
---

# Story 5.3 - Publish com permissao e ambiente

## Story

**Como** operador com permissao,  
**quero** **publicar** fluxo com **permissao** e **separacao** dev/stage/prod quando aplicavel,  
**para** FR24 e DoD publish (PRD).

## Acceptance Criteria

1. **Dado** draft aprovado e sandbox OK, **quando** publish e confirmado, **entao** versao **ativa** no ambiente alvo muda, com **audit** minimo (quem, quando) ligacao FR25.
2. Quem **nao** tem papel recebe **403** (FR7).
3. API (ex. `POST /v1/me/flows/{id}/publish`) com corpo `environment`; OpenAPI atualizado.

**Requisitos:** FR24, FR6, FR7.

## Tasks / Subtasks

- [ ] RBAC: papel para publish por ambiente (ex. so admin em prod).
- [ ] Transacao: ativar versao + registo audit append-only.
- [ ] Admin-web: confirmacao; ambiente visivel (UX-DR4 em erro).
- [ ] Testes 403; ATDD `test_epic5_story53_publish_atdd.py`.

## Party Mode (CS) - perspetivas

| Agente | Insight |
|--------|---------|
| **Winston** | Imutabilidade de versao publicada vs novo draft; sem overwrite silencioso. |
| **Mary** | FR24 + FR6/FR7; audit liga a 5.4. |
| **John** | Gate de qualidade antes de motor em prod. |
| **Sally** | Confirmacao destrutiva clara (publish prod). |
| **Amelia** | Idempotencia de publish repetido - 200 com mesma versao ou 409. |

## Advanced Elicitation (CS)

- **Pre-mortem:** dois publishes concorrentes - versionamento otimista (etag) ou lock.
- **Red team:** publish para ambiente errado - UI mostra ambiente em destaque.

## Validate Story (VS)

**Veredito:** **aprovada para ATDD/DS**.

### Party Mode (VS)

| Agente | VS |
|--------|-----|
| **Winston** | Audit obrigatorio no mesmo request de ativacao ou saga documentada. |
| **Amelia** | ATDD: POST publish 200/201 com header dev admin. |
| **Mary** | Teste 403 com role leitura. |

### Advanced Elicitation (VS)

- **Pre-mortem:** sandbox nao corrido - politica 409 ou aviso bloqueante.

### Checklist BMad (sintese)

| Categoria | Resultado |
|-----------|-----------|
| Seguranca | 403 sem papel; audit sem PII desnecessaria. |
| RLS | Fluxo e publish so no tenant. |

## Dev Notes - requisitos tecnicos

- Depende de **5.2**; integra com **2.2** para matriz de papeis.

## Testing Requirements

- ATDD: `v2/apps/api/tests/atdd/test_epic5_story53_publish_atdd.py`

## References

- `_bmad-output/planning-artifacts/epics.md` - Story 5.3

## Dev Agent Record

### Agent Model Used

_(preencher na implementacao)_

### Completion Notes List

### File List

---

## Change Log

- 2026-04-23: **[CS]** story individual; Party Mode + Advanced Elicitation.
- 2026-04-23: **[VS]** validada; `atdd_ready: true`.
- 2026-04-23: **[AT]** `test_epic5_story53_publish_atdd.py`.

---
story_key: 5-2-sandbox-preview
epic: epic-5
status: ready-for-dev
vs_validated: true
vs_date: 2026-04-23
atdd_ready: true
cs_completed: 2026-04-23
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 5-1-editor-fluxos-validacao
code_location: v2/apps/api, v2/apps/admin-web
---

# Story 5.2 - Sandbox e preview

## Story

**Como** operador,  
**quero** **testar** o fluxo em **sandbox** (preview) antes de publish,  
**para** FR23.

## Acceptance Criteria

1. **Dado** fluxo validado, **quando** executo teste em sandbox com fixture (mensagem, contacto stub se necessario), **entao** resultado (sucesso, falha, log minimo) fica **traceavel** e **nao** envia a **producao** (FR4).
2. Drawer de sandbox segue direcao lista|thread + lente (UX-DR1).
3. API sandbox (ex. `POST /v1/me/flows/{id}/sandbox-run`) documentada; flag ambiente **nao-prod** obrigatoria no motor de execucao.

**Requisitos:** FR23, FR38 (preparar sandbox tenant-scoped quando existir sandbox global).

## Tasks / Subtasks

- [ ] Runtime sandbox isolado (fila/worker ou modo sync dev-only documentado).
- [ ] Fixture de mensagem; correlacao de run id para UI.
- [ ] Admin-web: drawer preview; nao chamar endpoints de envio prod.
- [ ] Testes; ATDD `test_epic5_story52_sandbox_atdd.py`.

## Party Mode (CS) - perspetivas

| Agente | Insight |
|--------|---------|
| **Winston** | Barreira tecnica: credenciais Meta de sandbox vs prod separadas. |
| **Mary** | FR23 + FR4; traceabilidade explicita no AC. |
| **John** | Reduz risco de publish quebrar clientes. |
| **Sally** | UX-DR1: drawer coerente com inbox. |
| **Amelia** | Logs de sandbox rotulados; metricas separadas. |

## Advanced Elicitation (CS)

- **Pre-mortem:** sandbox dispara efeito real por bug - dupla checagem `environment=sandbox` no worker.
- **Red team:** utilizador forca header prod num run sandbox - servidor ignora cliente para side-effects.

## Validate Story (VS)

**Veredito:** **aprovada para ATDD/DS**.

### Party Mode (VS)

| Agente | VS |
|--------|-----|
| **Winston** | 5.1 valido obrigatorio antes de sandbox (ou 422 claro). |
| **Amelia** | ATDD: POST sandbox-run 200/202. |
| **Mary** | Evidencia de nao-producao testavel (mock Meta ou bucket isolado). |

### Advanced Elicitation (VS)

- **Pre-mortem:** timeout longo no sandbox - UX de cancelamento.

### Checklist BMad (sintese)

| Categoria | Resultado |
|-----------|-----------|
| Seguranca | Sem vazamento de dados prod para logs sandbox. |
| RLS | Runs escopados ao tenant. |

## Dev Notes - requisitos tecnicos

- Depende de **5.1**.

## Testing Requirements

- ATDD: `v2/apps/api/tests/atdd/test_epic5_story52_sandbox_atdd.py`

## References

- `_bmad-output/planning-artifacts/epics.md` - Story 5.2

## Dev Agent Record

### Agent Model Used

_(preencher na implementacao)_

### Completion Notes List

### File List

---

## Change Log

- 2026-04-23: **[CS]** story individual; Party Mode + Advanced Elicitation.
- 2026-04-23: **[VS]** validada; `atdd_ready: true`.
- 2026-04-23: **[AT]** `test_epic5_story52_sandbox_atdd.py`.

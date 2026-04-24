---
story_key: 5-4-versao-audit-materialidade
epic: epic-5
status: ready-for-dev
vs_validated: true
vs_date: 2026-04-23
atdd_ready: true
cs_completed: 2026-04-23
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 5-3-publish-permissao-ambiente
code_location: v2/apps/api, v2/apps/admin-web
---

# Story 5.4 - Versao e audit de materialidade

## Story

**Como** auditor ou admin,  
**quero** **historico** de versoes (ou diff minimo) de alteracoes **materiais**,  
**para** FR25 (compliance e debug).

## Acceptance Criteria

1. **Dado** publish ocorre, **entao** registo **append** com identidade e timestamp; rollback one-click **fora** de escopo salvo flag de produto; diff visual TBD.
2. Listagem de versoes por fluxo ordenada e paginada.
3. API (ex. `GET /v1/me/flows/{id}/versions`) documentada.

**Requisitos:** FR25.

## Tasks / Subtasks

- [ ] Tabela de versoes imutavel; referencia a snapshot JSON ou hash.
- [ ] Endpoint listagem; detalhe opcional por version id.
- [ ] Admin-web: timeline simples; export opcional.
- [ ] Testes; ATDD `test_epic5_story54_versions_audit_atdd.py`.

## Party Mode (CS) - perspetivas

| Agente | Insight |
|--------|---------|
| **Winston** | Append-only: sem UPDATE de linhas historicas; correcoes = nova versao. |
| **Mary** | FR25; ligacao a narrativa de compliance PRD. |
| **John** | Suporte a investigacao pos-incidente. |
| **Sally** | Datas e autor visiveis sem poluir inbox. |
| **Amelia** | Retencao de versoes - politica por tenant (fase 2). |

## Advanced Elicitation (CS)

- **Pre-mortem:** historico cresce sem limite - paginacao e arquivo.
- **Red team:** versao com dados sensiveis - mascarar em GET se necessario.

## Validate Story (VS)

**Veredito:** **aprovada para ATDD/DS**.

### Party Mode (VS)

| Agente | VS |
|--------|-----|
| **Winston** | Cada publish 5.3 cria linha de versao obrigatoriamente. |
| **Amelia** | ATDD: GET versions 200 com lista (pode vazia so com seed). |
| **Mary** | Identidade do autor = user id interno; GDPR em exports. |

### Advanced Elicitation (VS)

- **Pre-mortem:** migracao corrompe historico - backup antes de alterar schema de fluxo.

### Checklist BMad (sintese)

| Categoria | Resultado |
|-----------|-----------|
| Auditoria | Append-only; relogio confiavel (UTC). |
| RLS | Versoes so do tenant do fluxo. |

## Dev Notes - requisitos tecnicos

- Depende de **5.3** para eventos de publish.

## Testing Requirements

- ATDD: `v2/apps/api/tests/atdd/test_epic5_story54_versions_audit_atdd.py`

## References

- `_bmad-output/planning-artifacts/epics.md` - Story 5.4

## Dev Agent Record

### Agent Model Used

_(preencher na implementacao)_

### Completion Notes List

### File List

---

## Change Log

- 2026-04-23: **[CS]** story individual; Party Mode + Advanced Elicitation.
- 2026-04-23: **[VS]** validada; `atdd_ready: true`.
- 2026-04-23: **[AT]** `test_epic5_story54_versions_audit_atdd.py`.

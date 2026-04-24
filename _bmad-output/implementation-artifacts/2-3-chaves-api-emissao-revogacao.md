---
story_key: 2-3-chaves-api-emissao-revogacao
epic: epic-2
status: ready-for-dev
vs_validated: true
vs_date: 2026-04-23
atdd_ready: true
cs_completed: 2026-04-23
source: _bmad-output/planning-artifacts/epics.md
depends_on:
  - 2-2-matriz-papeis-permissoes
code_location: v2/apps/api, v2/apps/admin-web
---

# Story 2.3 - Chaves de API emissao e revogacao

## Story

**Como** **operador** ou **admin** com permissao,  
**quero** **criar, revogar e listar** chaves de integracao com **janela de coexistencia** controlada,  
**para** migrar integracoes sem downtime injustificado (FR8).

## Acceptance Criteria

1. **Dado** permissao explicita (FR7), **quando** emito nova chave e marco a antiga para revogacao agendada, **entao** ambas tem lifecycle e datas visiveis; revogacao respeita janela acordada.
2. **Nao** devolver segredo em plain apos criacao - apenas **uma vez** na resposta 201 (FR10).
3. Prefixo de rota alinhado ao CDA (ex. `POST /v1/me/api-keys`).

**Requisitos:** FR8, FR10, FR7. **NFRs:** NFR-SEC-02, NFR-SEC-03.

## Tasks / Subtasks

- [ ] Tabela `api_keys` (tenant_id, prefix, hash, status, expires_at, revoked_at) ou equivalente.
- [ ] POST criar (201 + secret once), GET listar (sem secret), POST/PATCH revogar com janela.
- [ ] Hashing seguro do secret; nunca logar valor completo.
- [ ] OpenAPI + testes integracao; ATDD `test_epic2_story23_chaves_api_atdd.py`.
- [ ] UI Integracoes: listagem honesta (UX-DR4).

## Party Mode (CS) - perspetivas

| Agente | Insight |
|--------|---------|
| **Winston** | Idempotencia e rate-limit em emissao - considerar NFR-SEC-02. |
| **Mary** | FR8/FR10 rastreados; coexistencia e requisito de negocio explicito. |
| **John** | Desbloqueia integradores e epico 7. |
| **Amelia** | Testes com header dev tenant + role com permissao; 403 sem papel. |
| **Sally** | Apos criar chave, UI mostra secret uma vez com aviso claro. |

## Advanced Elicitation (CS)

- **Pre-mortem:** utilizador perde secret - fluxo de rotacao sem expor antigos.
- **Red team:** enumeracao de prefixes - rate limit + audit.

## Validate Story (VS)

**Veredito:** **aprovada para ATDD/DS**.

### Party Mode (VS)

| Agente | VS |
|--------|-----|
| **Winston** | Armazenar so hash; rotacao documentada. |
| **Amelia** | ATDD exige 201 + campo secret ou key_prefix na criacao. |
| **Mary** | Janela de coexistencia refletida no modelo ou documentada como fase 2 com flag. |

### Advanced Elicitation (VS)

- **Socratic:** o que prova "uma vez"? - teste que falha se GET devolver secret.

### Checklist BMad (sintese)

| Categoria | Resultado |
|-----------|-----------|
| Seguranca | Secret nao repetivel; audit de emissao/revogacao. |
| RLS | tenant_id em todas as linhas. |

## Dev Notes - requisitos tecnicos

- Depende de **2.2** para checagem de papel na emissao.
- Autenticacao de chamadas com API key e historia relacionada (middleware) - definir se parte desta story ou follow-up.

## Testing Requirements

- ATDD: `v2/apps/api/tests/atdd/test_epic2_story23_chaves_api_atdd.py`

## References

- `_bmad-output/planning-artifacts/epics.md` - Story 2.3

## Dev Agent Record

### Agent Model Used

_(preencher na implementacao)_

### Completion Notes List

### File List

---

## Change Log

- 2026-04-23: **[CS]** story individual; Party Mode + Advanced Elicitation.
- 2026-04-23: **[VS]** validada; `atdd_ready: true`.
- 2026-04-23: **[AT]** `test_epic2_story23_chaves_api_atdd.py`.

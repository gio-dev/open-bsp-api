# Decisões pendentes ? ambiguidades do PRD (Party Mode)

**Data:** 2026-04-17  
**Contexto:** `bmad-create-prd` concluído para open-bsp-api. Esta tabela lista **regras ou temas que o PRD deixa abertos ou interpretáveis**, para **decisão explícita** antes ou durante backlog/arquitetura.

**Party Mode (vozes curtas):**  
**Mary** ? ambiguidade = risco de scope creep; cada linha deve ter **dono** e **data alvo**. **John** ? priorizar o que bloqueia **MVP/piloto** vs o que só afeta F2/F3. **Winston** ? marcar o que é **contrato técnico** (API, tenancy, filas) vs **UX**. **Victor** ? ligar cada linha a **risco comercial** ou ?ok assumir default?.

---

## Tabela: tema ? ambiguidade ? opções / pergunta de decisão ? onde o PRD já aponta

| # | Tema | O que é ambíguo | Pergunta(s) para decidir | O PRD já diz (pista) |
|---|------|-----------------|--------------------------|----------------------|
| 1 | **Fluxo MVP (regras)** | ?Cascata / múltipla escolha? vs motor genérico | O MVP exige **UI específica** (menus em árvore, botões numerados) ou basta **motor de regras + estados** com UX mínima definida depois? Profundidade máxima da árvore? | Chatbot **por regras**, gatilhos, sandbox; não prescreve widget de ?cascata?. |
| 2 | **Roteamento ?por setor?** | Setor como conceito de produto vs config do cliente | **Só** filas + etiquetas + regras **por tenant** (sem entidade ?setor? no core), ou modelo de dados **Departamento/Setor** no produto na v1? | Horizontal; setores verticais fora do núcleo; FR18?FR20 (filas, handoff). |
| 3 | **F2 ? Modelos de IA** | SLM vs LLM vs ?local? | Usar termos **SLM/LLM** no produto e roadmap? Política: **obrigatório** oferecer modelo local/pequeno ou **opcional** por plano? | ?Modelos locais/externos?; custo/conversa; sem obrigação explícita SLM. |
| 4 | **F2 ? Custo e comercialização** | Custo por ?agente? vs por uso | Faturação por **agente/bot nomeado**, por **volume/conversa**, ou **só metering** + contrato manual no início? | Metering, planos, custo médio/conversa; não fixa SKU ?por agente?. |
| 5 | **F2 ? Pipeline em cascata** | Cadeia de modelos/ferramentas | Uma **pipeline fixa** (ex.: classificador ? RAG ? resposta) é requisito de **F2** ou posição **arquitetural** pós-MVP? ?Cascata? entre IA local e paga é **produto** ou **integração**? | Agente desacoplado, políticas no produto; orquestração maior em **F3**. |
| 6 | **Stack do piloto** | Legado vs FastAPI em produção | Durante piloto, **única** stack em produção ou **coexistência**? Onde fica a **fonte da verdade** (webhook, envio)? Critério de **cutover**? | Passo 8: declarar runtime do piloto; migração com paridade. |
| 7 | **Billing MVP** | Automação vs manual | **Billing completo** no MVP ou **medição + cobrança manual** (PO/Stripe link) até validar motor económico? | Passo 8: metering como verdade; cobrança manual aceitável em pilotos. |
| 8 | **LGPD ? DSAR / export** | Produto vs processo | Até quando **export/DSAR** fica **assistido por ops** vs **self-serve no portal**? Gatilho de ?agora vira produto? (volume, auditoria)? | DSAR pode ser assistido no primeiro corte; FRs de pedido/export. |
| 9 | **Parceiro / revenda** | Canal direto only | **MVP** exclusivamente **B2B direto** ou já suportar **parceiro** (multi-tenant com permissões, billing)? | Passo 8: partner/revenda completo default fora salvo contrato. |
| 10 | **Onboarding** | White-glove vs self-serve | Prazo para **signup self-serve mínimo** estar **obrigatório** vs pilotos sempre guiados? | White-glove aceitável nos primeiros pilotos; self-serve como objetivo. |
| 11 | **Versionamento de fluxos** | Quão ?Git-like? | Versão é **rótulo + auditoria** ou **histórico completo, diff, rollback** na v1? | Publicação com auditoria; ?versionamento? nas jornadas; profundidade aberta. |
| 12 | **WABA / org** | Cardinalidade day one | Todo tenant **só 1 WABA** no MVP ou **N WABAs** desde o primeiro release? | Hierarquia org?WABA?número; não fixa ?1 só? no MVP na tabela FR. |
| 13 | **Embed / SSO** | Profundidade de integração | Apenas **iframe + OAuth tenant** ou também **SSO federado** (SAML/OIDC do cliente) **obrigatório** em algum tier? | OAuth/OIDC; embed; profundidade enterprise em aberto. |
| 14 | **F3 ? Orquestrador** | Quem opera o N8N | **N8N (ou similar) é serviço gerido pelo produto** ou **cliente integra o próprio** worker? | F3 piloto com orquestrador; detalhe operacional em aberto. |
| 15 | **Filas sob stress** | Noisy neighbour no canal | Sob **429 / pico Meta**, política é **fairness estrito entre tenants** ou **degradação global** documentada? Limiar de alerta compartilhado? | NFR fairness, quotas; **domínio de um tenant sobre filas** citado em pilot disturbance. |
| 16 | **Templates Meta** | Quem aprova | Aprovação de templates **100% no produto** vs fluxo híbrido com **Business Manager** até automatizar? | FR15 ciclo de vida de templates; profundidade de automação em aberto. |
| 17 | **Auditoria e retenção** | Duração mínima | **R meses** de log de auditoria e **p95** de consulta são fixados por **compliance** interno ou **calibrar por piloto** apenas? | NFR-OPS-03 com R e p95 exemplificativos. |
| 18 | **Critério ?piloto encerrado?** | Go/no-go | Lista **fechada** de gates (volume, incidentes, NPS, sponsor sign-off) na v1 do processo ou só **ad hoc**? | Passo 8: gates mensuráveis; percentagens não totalmente fixadas. |

---

## Próximo passo sugerido

1. **Marcar** cada linha: `MVP bloqueante` | `F2` | `F3` | `ops/comercial`.  
2. **Dono** (produto / eng / CS / financeiro).  
3. **Decisão** + data em reunião única ou em DARCI.

---

*Gerado em Party Mode (Mary, John, Winston, Victor) para fechar ambiguidades antes de épicos e ADRs.*

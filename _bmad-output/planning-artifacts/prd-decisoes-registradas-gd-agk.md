# Decisões registradas ? ambiguidades PRD (GD-AGK)

**Data do registo:** 2026-04-17  
**Última atualização:** 2026-04-17 (DSAR/LGPD, roadmap em 3 entregas, parceiro por fases, confirmação tópico 2)  
**Fonte:** respostas do decisor ao questionário de 18 tópicos (ambiguidades) + clarificações posteriores.

---

## Roadmap de entregas (visão do decisor)

O produto pretende ser **o mais completo possível**, organizado em **três entregas** sucessivas (cada uma pode ter MVP interno e aprofundamentos posteriores):

1. **Entrega 1 ? WhatsApp + agentes humanos + chatbot**  
   Canal WhatsApp, agentes humanos, chatbot **completo** com fluxos, roteiros e tudo o que for possível nessa camada (dentro do desenho técnico e das políticas Meta).

2. **Entrega 2 ? Agente inteligente**  
   Agente **treinável**, **configurável** e o mais **completo** possível (modelos, políticas, custos, fallbacks acordados nas decisões F2).

3. **Entrega 3 ? Orquestrador**  
   **Vários serviços**, base para **conectar e integrar rapidamente** (integrações administradas, serviços disponíveis ao cliente, APIs externas conforme decisão no tópico 14).

*Nota de gestão:* ?Completo? **não** implica colocar todas as capacidades no **primeiro go-live** de cada entrega ? evita explodir escopo sem releases intermediárias.

---

## 1 ? Fluxo MVP (regras)

**Decisão:** UX/UI bem definidas ficam para **outra etapa** com o agente de UI/UX; não bloquear o motor de regras/estados por especificação visual do MVP.

---

## 2 ? Roteamento ?por setor? / categorias

**Decisão:** Cada **agente humano** pertence a uma **categoria**; cada conta tem uma **categoria base** que **não pode ser removida**; a **fila** forma-se com base nessa categoria.

**Confirmação (2026-04-17):** o decisor **confirma** a direção; o **modelo de dados** em backlog deve esclarecer: categoria base **imutável vs renomeável**; **um agente só numa categoria** vs várias; regras de migração entre categorias.

*Nota de análise:* alinha ?setor? a **categoria + fila** (entidade Categoria, obrigatoriedade da base, vínculo agente?categoria em FR/epics).

---

## 3 ? F2: modelos de IA (SLM / LLM / local)

**Decisão:** Pode usar os termos **SLM/LLM** no produto e roadmap. **Modelo local/pequeno** é o **default** sempre que o cliente **não** configurar um modelo pago. **Área administrativa** para **cadastrar novos modelos** (e afins).

---

## 4 ? F2: custo e comercialização

**Decisão:** Faturamento do Agente Inteligente por **ativação**; pode existir componente **por volume/conversa**; **ilimitado no início** da operação.

---

## 5 ? F2: pipeline em cascata

**Decisão:** Pipeline **não fixa** ? outros tipos **habilitáveis**; arquitetura pode ser refinada depois. **Fallback:** se IA paga falhar ? **local**; se não houver outra ativa ? usa-se **local**.

---

## 6 ? Stack do piloto

**Decisão:** **Direto FastAPI** (sem dependência de piloto em stack legada como fonte da verdade).

---

## 7 ? Billing no MVP

**Decisão:** Planos **mensal** ou **anual com desconto**; cada etapa/fase com **acréscimo de valor**; planos com limites (ex.: agentes humanos, agentes inteligentes, integrações) **atualizados na conta** ao contratar; plano **enterprise** com **admin a definir valor e limites** por negociação; **admin pode alterar limites por empresa** sem alterar o plano ?global?.

---

## 8 ? LGPD: DSAR / export (decisão alinhada à boa prática)

**Aviso:** orientação de **produto e governança** ? **não substitui** parecer jurídico; validar prazos, papel de controlador/operador nos contratos e casos limite com **DPO/advogado**.

### O que significa

- **DSAR** = pedido da pessoa sobre **os seus dados** (acesso, correção, eliminação, portabilidade, etc.) ? direitos do **titular** (LGPD).
- **Export** = **pacote** de dados gerado para cumprir o pedido ou apoiar o DPO.

### Decisão registrada: modelo **híbrido** (recomendado)

| Camada | Conteúdo |
|--------|----------|
| **Base** | **Portal/workflow**: abrir pedido, identificar titular e âmbito, **estado** (recebido / em análise / concluído), **trilho de auditoria**. |
| **Self-serve onde seguro** | Export e respostas **padronizadas** quando o fluxo estiver **mapeado** e **validado** (dados e retenção conhecidos). |
| **Assistido obrigatório** | Pedidos **complexos**, dúvida de **identidade**, **litígio**, volume **manifestamente excessivo**, cruzamentos difíceis ? **ops/DPO** com registo. |
| **Sempre** | **Registos** (quem, quando, o quê, base legal quando aplicável), **revisão** de incidentes e coerência com **subprocessadores** e contratos. |

**Prazos legais:** o produto pode ter **alertas** e SLA interno; **números legais** não são fixados neste documento ? conforme regulamentação/ANPD e parecer jurídico.

**Estado:** decisão de **princípio** fechada em **híbrido**; **gatilhos** finos (ex.: quando expandir self-serve) podem ser calibrados com volume e auditoria.

---

## 9 ? Parceiro / revenda

**Decisão:** **O mais completo possível** ? projeto grande; modelo **parceiro/revenda** integrado na ambição (não só B2B direto minimal).

**Alinhamento com PRD anterior:** o passo 8 do PRD tinha sugerido **parceiro completo** fora do núcleo do piloto **por defeito**; a decisão aqui é **pensar grande** e **completar ao longo do tempo**.

**Nota de roadmap:** ?MVP parceiro? vs **fase partner 1.5** deve ser explícito no backlog ? **capacidades de parceiro** (permissões, billing, multi-tenant de revenda) podem **entrar em ondas** para não **explodir a primeira release**; a **direção** é **completo**, não necessariamente **tudo no dia um**.

---

## 10 ? Onboarding

**Decisão:** Onboarding/setup **feito pelo decisor**; **cliente** só em pontos operacionais: cadastrar agentes humanos, criar/editar fluxos de chatbot, treinar/modificar agente inteligente.

---

## 11 ? Versionamento de fluxos

**Decisão:** **Ligação ao Git**; **máxima informação** configurável sobre o que guardar em **logs**.

---

## 12 ? WABA por organização

**Decisão:** Tenant pode ter **várias WABAs** conforme **plano** e **edições no cadastro** do cliente após aquisição do plano.

---

## 13 ? Embed e SSO

**Decisão:** **SSO federado**; definir **melhor abordagem** de implementação em desenho técnico (SAML/OIDC, etc.).

---

## 14 ? F3: orquestrador

**Decisão:** Integrações **criadas e cadastradas** pelo lado administrativo como **?serviço disponível?**; cliente **escolhe como usar**; **agente inteligente** e **chatbot** podem usar o fluxo; cliente pode ter **APIs/serviços externos** a invocar.

---

## 15 ? Filas sob stress (429 / pico Meta)

**Decisão:** **Fairness rígido entre tenants**; **alertas** para **admin** e **cliente**.

---

## 16 ? Templates Meta

**Decisão:** Fluxo **híbrido**; **automatizar** seria o cenário ideal.

---

## 17 ? Auditoria e retenção de logs

**Decisão:** **Calibrar** (não fixar R/p95 como regra imutável antes de dados).

---

## 18 ? Critério ?piloto encerrado?

**Decisão:** Deixado **a critério indicativo** do analista.

### Gates indicativos sugeridos (não vinculativos até aprovação)

1. **Duração mínima** no piloto (ex.: 60?90 dias) e **volume mínimo** de mensagens/conversas para amostra válida.  
2. **Incidentes de canal** (Meta/plataforma) abaixo de limiar acordado vs baseline.  
3. **Sign-off** explícito do **sponsor/comprador** (continuar, expandir, ou encerrar).  
4. **Revisão** de North Star / métricas de valor (não só adoção).  
5. Opcional: **NPS** ou entrevista estruturada com operadores.

---

*Documento de rastreabilidade para backlog, PRD (edições futuras) e ADRs conforme processo da equipa.*

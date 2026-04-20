---
title: "Product Brief: Autocontrollerbot"
status: "complete"
created: "2026-04-17"
updated: "2026-04-17"
inputs:
  - "_bmad-output/planning-artifacts/research/platform-MR-DR-TR-aprofundado-2026-04-17.md"
  - "Conversa guiada CB (Mary) ? checklist D.2, MVP em fases (produto horizontal)"
document_output_language: "pt-BR"
---

# Product Brief: Autocontrollerbot

## Resumo executivo

O **Autocontrollerbot** é uma **plataforma multitenant** para organizações que precisam de **WhatsApp Business** com **vários atendentes e filas por setor ou categoria**, **fluxos conversacionais** (estilo chatbot com múltiplas opções, dentro do permitido pela Meta) e, em fases seguintes, **agentes de IA** e **integrações com sistemas legados** ? como **ERPs** que hoje não conversam com o WhatsApp.

**Cenário ilustrativo (não fixa vertical):** uma **organização** cujo **ERP ou sistema de registo** não integra nativamente com WhatsApp: **documentos ou pedidos** enviados pelos **contactos** pelo canal não entram no sistema oficial de forma **automática**, gerando retrabalho e risco de perda. O produto posiciona-se como **camada de orquestração** entre **Meta / motor de mensagens (OpenBSP como núcleo técnico)** e **processos do cliente**, com **liberação de funcionalidades por plano e por conta** ? incluindo **fluxos configuráveis** semelhantes a chatbots padrão. O **primeiro piloto** pode ser em qualquer setor compatível com este padrão (serviços, institutionais, indústria leve, etc.).

**Porquê agora:** adoção massiva de WhatsApp B2B2C, expectativa de **automação responsável**, e espaço para **parceiros tecnológicos** que entreguem **go-live rápido** com **governança** (aprovação de agentes, LGPD no Brasil).

---

## O problema

Organizações **já usam WhatsApp** para falar com clientes ou cidadãos, mas o **sistema de registo oficial** (ERP, CRM interno, protocolo) **fica à parte**. Em especial:

- **Documentos ou pedidos** chegam pelo telemóvel **sem ligação automática** ao processo certo no sistema de destino.
- **Várias equipas** (setores, unidades) precisam de **partilhar o mesmo número** sem caos ? **setores/categorias** e **filas** tornam-se críticos.
- **Automação** tipo chatbot é desejável, mas **não pode ser igual para todos**: deve ser **controlada por plano** e por **conta**, para alinhar **custo, risco e maturidade** do cliente.

**Comprador que assina (B2B):** tipicamente **direção/gestão** e/ou **TI** ? perfis com preocupações distintas (negócio vs operação e segurança).

---

## A solução

Uma **plataforma** que oferece:

1. **Base (primeira onda de valor):** **multitenant**; **WhatsApp multi-agente** no mesmo número com **setores/categorias**; **conversas com fluxos** e **múltiplas opções**, explorando **o máximo permitido pelas políticas e APIs Meta**; **embed** (iframe) para **conversa + configurações leves** em sistemas de terceiros.  
2. **Segunda fase:** **agente inteligente** que **evolui conforme o negócio** (aprendizagem e políticas definidas por produto ? não ?magia?).  
3. **Terceira fase:** **integrador** com **sistemas terceiros**, **conectado ao agente** e a fluxos de documento/evento.

Por baixo, o desenho assume um **motor de mensagens e dados** compatível com **OpenBSP** (WhatsApp Cloud API, organizações, mensagens, webhooks), e **automação de integração** (ex.: **N8N** ou equivalente) onde fizer sentido **custo/benefício**.

---

## O que diferencia

| Diferencial | Nota |
|-------------|------|
| **Governança + planos** | Fluxos estilo chatbot e capacidades **ligadas a plano/conta** ? clareza comercial e técnica. |
| **Encaixe no sistema do cliente** | **Iframe** e integrações ? o WhatsApp não fica ?ilha?. |
| **Faseamento honesto** | MVP forte em **canal + fluxos + multitenant**; IA e ERP como **ondas**, não promessa única no dia um. |
| **Brasil** | **LGPD** e **transparência de custo Meta** como princípios; **aspiração** a **Partner Meta** quando o volume e a operação justificarem. |

*Vantagem competitiva realista:* **velocidade de entrega** + **pacotes** claros + **confiança** em contexto sensível (documentos, dados de titulares).

---

## Para quem é

| Papel | O que precisa |
|-------|----------------|
| **Direção / negócio** | Reduzir fricção e reclamações; visibilidade de atendimento. |
| **TI** | Integração controlada, segurança, **menos trabalho manual** de ponta entre canais. |
| **Operações / atendimento** | Filas claras, fluxos, **menos erro** na triagem de pedidos e documentos. |

**Nota:** O **primeiro cliente piloto** é escolhido por **fit comercial e técnico**, não por setor fixo; a plataforma é pensada para **reutilização** (agências, ISV, várias organizações).

---

## Critérios de sucesso

- **Principal (definido por ti):** **satisfação do cliente**.  
- **Indicadores operacionais** (ex.: tempo até documento no ERP, retrabalho): **PRD**, não este brief.  
- **Negócio (fornecedor):** adopção de **planos superiores**, **retention**, e redução de **custo de suporte** por tenant.

---

## Âmbito e roadmap (visão MVP ? escala)

| Fase | Foco |
|------|------|
| **1 ? Base** | Multitenant; WA **multi-agente** / setores; **fluxos conversacionais** com múltiplas opções (limite Meta); iframe **chat + config leve**; **gates por plano/conta** para fluxos. |
| **2 ? IA** | Agente inteligente com **evolução dependente do negócio** e **critérios de aprovação** (só B2B ou B2B + cliente final, conforme cenário). |
| **3 ? Integração** | **Integrador** com sistemas terceiros **ligado ao agente** e a eventos de documento/mensagem. |

**Explícito fora do MVP inicial:** prometer **integração ERP completa** e **IA autónoma sem supervisão** no primeiro dia.

---

## Visão (2?3 anos)

Tornar-se uma **referência regional** para **WhatsApp Business operacional a sério** (B2B/B2B2C): **multitenant**, **fluxos e IA com trilho**, **integrações modulares**, e **relação Meta** madura (**Partner** onde fizer sentido).

---

## Abordagem técnica (alto nível)

- **Motor de mensagens / API WhatsApp:** núcleo alinhado a **OpenBSP**.  
- **Plataforma própria:** **portal**, **planos**, **liberação de fluxos**, **embed**.  
- **Integrações:** automação (ex. N8N) e conectores; **webhooks** e APIs conforme o desenho já estudado no repositório.

---

## Conformidade e contexto Brasil

- **LGPD** para dados de titulares e interlocutores.  
- **Políticas Meta** (templates, janelas, categorias) como **restrições de produto**, não detalhe opcional.

---

## Notas da revisão interna (painel)

**Cético:** Proxies mensuráveis ficam no **PRD** (acordo com GD-AGK). Clientes em **compras públicas** ou **enterprise** podem implicar **edital, procurement ou ciclo longo** ? mesmo sem prazo interno teu, o **cliente** pode atrasar decisão.  
**Oportunidade:** **Pacotes de extensão vertical sob demanda** (fluxos + checklist LGPD + integrações típicas do setor, quando contratado). **Parceria com integradores do ERP/sistema do cliente** (qualquer vertical).  
**Mudança organizacional:** **Negócio** e **TI** com **KPIs diferentes** ? o brief deve sustentar **dois discursos** no mesmo deck.

---

*Brief fechado em modo guiado (Mary / CB), 2026-04-17.*

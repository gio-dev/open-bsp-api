---
title: "Product Brief: Autocontrollerbot"
status: "complete"
created: "2026-04-17"
updated: "2026-04-17"
inputs:
  - "_bmad-output/planning-artifacts/research/platform-MR-DR-TR-aprofundado-2026-04-17.md"
  - "Conversa guiada CB (Mary) ? checklist D.2, faculdade, MVP em fases"
document_output_language: "pt-BR"
---

# Product Brief: Autocontrollerbot

## Resumo executivo

O **Autocontrollerbot** é uma **plataforma multitenant** para organizações que precisam de **WhatsApp Business** com **vários atendentes e filas por setor ou categoria**, **fluxos conversacionais** (estilo chatbot com múltiplas opções, dentro do permitido pela Meta) e, em fases seguintes, **agentes de IA** e **integrações com sistemas legados** ? como **ERPs** que hoje não conversam com o WhatsApp.

A **primeira narrativa de referência** é uma **faculdade** cujo **ERP** não integra com WhatsApp: **documentos enviados pelos alunos pelo canal** não chegam ao sistema académico de forma **automática**, gerando retrabalho e risco de perda de informação. O produto posiciona-se como **camada de orquestração** entre **Meta / motor de mensagens (OpenBSP como núcleo técnico)** e **processos institucionais**, com **liberação de funcionalidades por plano e por conta** ? incluindo **fluxos configuráveis** semelhantes a chatbots padrão.

**Porquê agora:** adoção massiva de WhatsApp em contextos institucionais, expectativa de **automação responsável**, e espaço para **parceiros tecnológicos** que entreguem **go-live rápido** com **governança** (aprovação de agentes, LGPD no Brasil).

---

## O problema

Instituições (e muitas empresas) **já usam WhatsApp** para falar com alunos, clientes ou cidadãos, mas o **sistema de registo oficial** (ERP, académico, protocolo) **fica à parte**. Em especial:

- **Documentos** chegam pelo telemóvel **sem ligação automática** ao processo certo no ERP.
- **Várias equipas** (secretarias, setores) precisam de **partilhar o mesmo número** sem caos ? **setores/categorias** e **filas** tornam-se críticos.
- **Automação** ?tipo chatbot? é desejável, mas **não pode ser iguais para todos**: deve ser **controlada por plano** e por **conta**, para alinhar **custo, risco e maturidade** do cliente.

**Comprador que assina (âncora faculdade):** tipicamente **Reitoria** e/ou **TI** ? perfis com preocupações distintas (missão institucional vs operação e segurança).

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

*Vantagem competitiva realista:* **velocidade de entrega** + **pacotes** claros + **confiança** em contexto sensível (documentos, instituições).

---

## Para quem é

| Papel | O que precisa |
|-------|----------------|
| **Reitoria / direção** | Reduzir fricção e reclamações; visibilidade de atendimento. |
| **TI** | Integração controlada, segurança, **menos trabalho manual** de ponta entre canais. |
| **Operações / secretarias** | Filas claras, fluxos, **menos erro** na triagem de documentos. |

**Nota:** O **teu** cliente inicial é a **faculdade**; a plataforma no entanto é pensada para **reutilização** (agências, ISV, outras instituições).

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

Tornar-se a **referência regional** para **?WhatsApp institucional sério?**: **multitenant**, **fluxos e IA com trilho**, **integrações modulares**, e **relação Meta** madura (**Partner** onde fizer sentido).

---

## Abordagem técnica (alto nível)

- **Motor de mensagens / API WhatsApp:** núcleo alinhado a **OpenBSP**.  
- **Plataforma própria:** **portal**, **planos**, **liberação de fluxos**, **embed**.  
- **Integrações:** automação (ex. N8N) e conectores; **webhooks** e APIs conforme o desenho já estudado no repositório.

---

## Conformidade e contexto Brasil

- **LGPD** para dados de alunos e interlocutores.  
- **Políticas Meta** (templates, janelas, categorias) como **restrições de produto**, não detalhe opcional.

---

## Notas da revisão interna (painel)

**Cético:** Proxies mensuráveis ficam no **PRD** (acordo com GD-AGK). **Compras públicas** em educação podem implicar **edital e prazo** ? mesmo sem prazo teu interno, o cliente pode ter **ciclo de compra longo**.  
**Oportunidade:** **Pacote vertical ?educação?** (fluxos + checklist LGPD + integrações típicas). **Parceria com integradores do ERP** da faculdade.  
**Mudança organizacional:** **Reitoria** e **TI** com **KPIs diferentes** ? o brief deve sustentar **dois discursos** no mesmo deck.

---

*Brief fechado em modo guiado (Mary / CB), 2026-04-17.*

---
title: "Product Brief Distillate: Autocontrollerbot"
type: llm-distillate
source: "product-brief-autocontrollerbot.md"
created: "2026-04-17"
purpose: "Contexto denso para PRD e próximas fases"
---

# Distillate ? Autocontrollerbot

## Identidade e naming

- Codinome: **autocontrollerbot**; naming comercial em aberto (sugestões: Autocontroller; nomes neutros para não ficar preso a ?bot?).
- Sem restrição de marca nem prazo fixo declarado pelo GD-AGK.

## Requisitos explícitos capturados

- **Fluxos tipo chatbot padrão** com **criação/opções** sujeitas a **liberação por plano e/ou por conta**.
- **Multitenant** em todo o desenho.
- **OpenBSP** como motor de WhatsApp ?por baixo?; **N8N** (ou equivalente) como camada de integração quando aplicável.
- **Iframe v1:** conversa + **config leve** (quick replies, filas, etc.), não painel admin completo no embed inicial.
- **Brasil primeiro**; LGPD como eixo.
- **Custo Meta:** começar com **repasse transparente**; **aspiração Partner** quando viável.
- **Aprovação de agente IA:** cenários (a) só cliente B2B e (c) B2B + cliente final ? **produto flexível**.

## Primeiro cliente âncora

- **Faculdade**; ERP **sem** integração nativa com WhatsApp.
- Dor: **documentos de alunos** via WhatsApp **não entram no ERP automaticamente**.
- Quem assina: **Reitoria** e/ou **TI**.

## Métricas

- Brief: foco em **satisfação do cliente**.
- **Proxies operacionais:** só no **PRD** (acordo com GD-AGK).

## Roadmap MVP (ordem explícita do GD-AGK)

1. Base: multitenant + WA **multi-agente** mesmo número (**setor/categoria**) + **fluxos** com múltiplas opções (**máximo Meta**).
2. Agente IA que **aprende conforme o negócio** (política de produto a definir).
3. Integrador **terceiros** **ligado ao agente** inteligente.

## Contexto técnico (overflow)

- Relatório MR/DR/TR: `_bmad-output/planning-artifacts/research/platform-MR-DR-TR-aprofundado-2026-04-17.md`.
- Docs modulares OpenBSP: `docs/modular/` (webhooks `LIMIT 3`, triggers, etc.).
- **Risco:** `notify_webhook` com limite de 3 destinos por disparo ? fan-out ou evolução de schema se integrações exigirem mais.

## Ideias rejeitadas / não MVP

- Integração ERP ?completa no dia um? ? **fora** do MVP explícito.
- IA sem trilho de aprovação ? **incompatível** com narrativa de risco institucional.

## Perguntas em aberto (para PRD)

- Nome comercial final.
- **Métricas de sucesso** além de satisfação (obrigatório para contratos/compras públicas?).
- **Fluxos por plano:** matriz exata (o que cada plano desbloqueia).
- Integração prioritária com **qual** ERP na faculdade âncora.

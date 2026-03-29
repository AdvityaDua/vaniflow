# Vani-Flow — Design Document (Prototype)

**Version:** 1.0 · **Aligned with:** PRD v2.0 · **Frontend:** React/Next.js, Tailwind CSS, shadcn/ui

---

## 1. Purpose

This document defines a **practical, minimal** implementation plan for a **hackathon prototype** of Vani-Flow: a voice-first, multi-agent system that resolves enterprise-style complaints, **adapts when UI/docs drift**, and **teaches users** the new steps—while keeping a **structured audit trail** and a **local-first** inference story where feasible.

---

## 2. Problem & Success Criteria (Prototype)

| Goal | Prototype interpretation |
|------|---------------------------|
| End-to-end resolution | One scripted path works: complaint → plan → execute → customer reply |
| UI drift & learning | Mock “enterprise web” changes; Agent 5 discovers new path; memory speeds repeat |
| Auditability | Every major step visible in a simple log (who/what/when/verdict) |
| Voice-first | Mic capture → STT → same pipeline as text (can stub STT in dry runs) |

**Non-goals for v0:** Full CRM/ERP integrations, production SLA automation, mobile apps, vision-only UI understanding, multi-tenant hardening.

---

## 3. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Web UI (Next.js + shadcn + Tailwind)                           │
│  • Customer widget: voice + chat                                │
│  • Ops dashboard: metrics + audit log                             │
│  • L2 view: escalation + recovery plan preview                    │
│  • Dev: mock “company app” + drift toggle (rename/move control) │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS / WebSocket (optional)
┌────────────────────────────▼────────────────────────────────────┐
│  API (FastAPI)                                                   │
│  • Sessions, streaming responses, file upload for audio          │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│  Orchestrator (LangGraph or thin state machine)                  │
│  Router → Knowledge → [Judge ↔ Action] → optional Learner        │
└───┬─────────────┬──────────────┬──────────────┬──────────────────┘
    │             │              │              │
    ▼             ▼              ▼              ▼
 PostgreSQL   Chroma/FAISS    Mock/API      “Mock ERP Web”
 (sessions,   (RAG + memory   adapters      (Playwright or
  audit)       embeddings)                    in-app iframe)
```

**Prototype rule:** Prefer **one happy path** fully wired; other intents return a clear “escalation” or generic message with audit entry.

---

## 4. Five-Agent Mesh (Behavioral Contract)

| Agent | Role | Prototype implementation |
|-------|------|---------------------------|
| **A1 Router** | STT, sentiment, intent, priority | Whisper/Bhashini or typed text; small classifier or LLM prompt; output JSON schema from PRD |
| **A2 Knowledge** | RAG + learning memory → resolution plan | Retrieve from vector store + `Adaptive Memory` table/store; single “refund” policy doc for demo |
| **A3 Action** | Execute plan (API/UI steps) | Sequential steps against **mock services** + **Playwright** or **DOM API** on mock app |
| **A4 Judge** | Approve / block / escalate | Rule-based + LLM: policy IDs, PII flags, anomaly heuristics; write audit row |
| **A5 Learner** | On persistent UI failure: analyze, explore DOM, rebuild flow, save memory, user text | DOM parse + text similarity; retry loop; persist `Adaptive Memory`; return guidance string |

**Flow:** A1 → A2 → (A4 approves) → A3 loops with A4 on each risky step if needed. On **drift failure**, A3 triggers A5; A5 updates memory and returns guidance to the customer channel.

---

## 5. Data Layer

- **PostgreSQL:** `complaints`, `sessions`, `audit_log` (verdict, reason, refs), optional `users` for demo.
- **Vector store (Chroma/FAISS):** KB chunks + optional embeddings for **adaptive memory** (issue type + flow text).
- **PRD-aligned payloads:** Complaint object, Adaptive Memory object—use as API JSON contracts between agents and UI.

---

## 6. Frontend Design (Minimal, shadcn + Tailwind)

**Principles:** Dense but calm; single accent; clear hierarchy; no decorative noise. Use shadcn **Card**, **Button**, **Input**, **ScrollArea**, **Badge**, **Tabs**, **Sheet/Dialog**, **Sonner** toasts.

| Surface | Purpose | Key components |
|---------|---------|----------------|
| **Customer widget** | Mic + transcript + chat thread + streaming assistant | Card, scrollable messages, input, optional `AudioRecorder` pattern |
| **Ops dashboard** | Resolution rate, SLA-style counters (mock), audit table | Table or Data table, filters, Badge for status |
| **L2 escalation** | View case + “Recovery Plan” + one-click approve (mock) | Dialog, markdown or structured plan |
| **Mock admin / drift lab** | Toggle rename button, hide old path | Switch, labels—drives backend mock config |

**Routing (suggested):** `/` widget demo · `/ops` dashboard · `/l2/[id]` escalation · `/lab` drift controls.

---

## 7. Backend API (Sketch)

- `POST /sessions` — start session  
- `POST /sessions/{id}/message` — text (and optional audio multipart)  
- `GET /sessions/{id}/events` — SSE or poll for agent steps (demo visibility)  
- `GET /audit` — list with filters  
- `POST /lab/drift` — set mock UI config (dev only)  

Keep payloads aligned with PRD §6.

---

## 8. Security & Privacy (Story for Judges)

- Document that **SLMs run locally** in the target architecture; prototype may use **one** cloud API with redaction for speed—call out in README.  
- Audit log stores **no raw secrets**; mask IDs in UI.

---

## 9. Demo Script (Engineering Mapping)

1. User: “I haven’t received my refund.”  
2. Lab: rename/refactor “Refund” control.  
3. A3 fails → A5 runs → success + guidance text.  
4. Repeat same utterance → A2 hits memory → no failure path.

Automate this as an **E2E checklist** in the TODO file.

---

## 10. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Agent 5 DOM brittleness | Constrain mock app to stable structure; semantic match on visible text |
| Time | Stub agents first, then replace core with LLM/RAG |
| Judge false positives | Start with rules; add LLM only for demo narrative |

---

## 11. Out of Scope (This Design)

Vision models, real enterprise SSO, production load, full Bhashini/Whisper tuning, federated learning.

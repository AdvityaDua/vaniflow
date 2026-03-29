# Vani-Flow — Prototype TODO (Detailed)

Use this as a step-by-step execution list. Order is **recommended**, not absolute where noted.

---

## Phase A — Foundation

### A1. Repository & standards
- [ ] Initialize monorepo or single repo with clear folders: `apps/web` (Next.js), `services/api` (FastAPI), `packages/shared` (optional TS types matching PRD JSON).
- [ ] Add `.env.example` for API keys, DB URL, model endpoints; document **local vs cloud** model usage.
- [ ] Pin Node and Python versions (e.g. `.nvmrc`, `pyproject.toml` or `requirements.txt`).

### A2. Frontend shell (Next.js + Tailwind + shadcn)
- [ ] Create Next.js app with App Router; install and configure Tailwind.
- [ ] Initialize shadcn/ui (`components.json`), add base theme (minimal: neutral background, one primary color).
- [ ] Add layout: optional top nav with links to Widget / Ops / Lab; font and spacing consistent across pages.

### A3. Backend shell (FastAPI)
- [ ] Scaffold FastAPI app with CORS for the web origin, health check `GET /health`.
- [ ] Add Pydantic models for Complaint, Adaptive Memory, Audit entry (match PRD §6).
- [ ] Stub `POST /sessions` and `POST /sessions/{id}/message` returning fixed JSON until orchestrator exists.

### A4. Database & persistence
- [ ] Run PostgreSQL locally (Docker Compose recommended).
- [ ] Migrations: tables for `sessions`, `complaints`, `audit_log`, `adaptive_memory` (or embed memory in JSON column for speed).
- [ ] Wire SQLAlchemy/asyncpg (or equivalent) from FastAPI.

---

## Phase B — Mock “Company Systems”

### B1. Mock ERP / web app
- [ ] Build a minimal multi-page or single-page **mock internal app** (can be Next.js route `/mock-app` or separate static HTML) with: Dashboard, Billing, Claims, a button **Refund** (later renamed to **Process Reimbursement** via lab toggle).
- [ ] Expose **programmatic drift**: env or API flag to change labels, `data-testid`, or routes so Agent 3 can fail deterministically before Agent 5 fixes the path.

### B2. Execution bridge for Agent 3
- [ ] Choose **Playwright** (headless) or **in-process DOM** if mock is same-origin iframe—pick one and document it.
- [ ] Implement **one golden workflow**: e.g. navigate Billing → Claims → click target button; return success/failure + logs.

---

## Phase C — Orchestrator

### C1. State machine / LangGraph
- [ ] Model states: `ROUTED`, `PLANNED`, `JUDGE_PENDING`, `EXECUTING`, `HEALING`, `DONE`, `ESCALATED`, `FAILED`.
- [ ] Implement graph edges: A1→A2→A4→A3; on failure loop; A3→A5 on drift signal; A5→memory→DONE.
- [ ] Persist each transition to `audit_log` with timestamps and agent name.

### C2. Session & streaming (optional but high impact for demo)
- [ ] `GET /sessions/{id}/events` as SSE: emit agent labels (“Router: intent=refund_status”) for UI timeline.

---

## Phase D — Agents (incremental)

### D1. Agent 1 — Router
- [ ] Input: audio file or text. If audio: call Whisper local or Bhashini; if unavailable, allow **text-only path** for CI.
- [ ] Output JSON: `transcript`, `intent`, `category`, `sentiment_score`, `priority` (rule-based priority from keywords acceptable for prototype).
- [ ] Map intents to internal `complaint_id` and store Complaint object.

### D2. Agent 2 — Knowledge
- [ ] Ingest **small KB** (Markdown): refund policy, SLA text—chunk and embed into Chroma or FAISS.
- [ ] Query **Learning Memory** (vector + structured filter by `issue_type`).
- [ ] Produce `resolution_plan`, `matched_policy_ids`, `confidence_score`; if low confidence → escalate in Judge.

### D3. Agent 4 — Judge (implement before full Action complexity)
- [ ] Rules: allowed actions whitelist for demo; block destructive ops; require escalation if `confidence_score` < threshold.
- [ ] Output `verdict`, `reason`, append **audit_entry** to DB.
- [ ] Optional: second pass with small LLM for natural-language reason string.

### D4. Agent 3 — Action
- [ ] Map resolution plan steps to **registered tools** (API mocks: e.g. `check_refund_status`, `submit_ticket`).
- [ ] On tool failure: retry N times; classify error (503 vs element not found).
- [ ] On **element not found / UI mismatch**: emit structured event to trigger Agent 5 (do not infinite loop).

### D5. Agent 5 — Self-healing UI
- [ ] Input: failure log, current DOM snapshot or Playwright page handle, recovery context.
- [ ] **Failure analysis:** detect missing selector vs network error.
- [ ] **Exploration:** walk visible links/buttons; rank by text similarity to “refund”, “reimbursement”, “claims”.
- [ ] **Workflow reconstruction:** build ordered steps; **validate** by executing once in headless browser.
- [ ] **Memory:** upsert Adaptive Memory object; embed `new_flow` text for RAG.
- [ ] **User guidance:** template + LLM to produce one short paragraph (PRD example wording).

---

## Phase E — Frontend Features

### E1. Customer widget (`/`)
- [ ] Chat UI with shadcn **Card** + **ScrollArea**; message bubbles (user / assistant).
- [ ] Mic button: capture audio → upload to `/sessions/{id}/message`; show transcript from server.
- [ ] Display **guidance** messages when Agent 5 returns `user_guidance`.
- [ ] Show compact **timeline** of agent steps if SSE/poll is implemented.

### E2. Ops dashboard (`/ops`)
- [ ] KPI cards: mock counts (resolved, escalated, avg time)—can be computed from DB or static for first pass.
- [ ] **Audit table**: time, complaint id, intent, verdict, short reason; link to detail.

### E3. L2 view (`/l2/[id]` or modal from ops)
- [ ] Show complaint summary + **Recovery Plan** JSON rendered as readable sections.
- [ ] “Approve” button calling `POST` stub that marks escalation resolved (demo only).

### E4. Drift lab (`/lab`)
- [ ] Toggles: rename button, move section, or hide old path—bound to backend `/lab/drift`.
- [ ] Short instructions on screen for judges: steps 1–4 of demo script.

---

## Phase F — Integration & Demo Hardening

### F1. Wire end-to-end
- [ ] Single script: create session → send refund complaint → verify audit trail and final assistant message.
- [ ] Second run with drift **on** first time (failure + heal); **off** or memory warm for second utterance (instant path).

### F2. Error paths
- [ ] Simulated 503: Action fails 3× → Recovery Plan + Judge `escalate` + L2 visibility.
- [ ] Ensure UI never hangs: timeouts on Playwright and LLM calls with user-facing message.

### F3. Docker (optional but helpful)
- [ ] `docker-compose`: Postgres, API, web; document `docker compose up` for judges.

---

## Phase G — Polish & Judging Fit

### G1. README
- [ ] Problem one-liner, architecture diagram (link to DESIGN doc), how to run, demo script checklist, what is mocked.

### G2. Audit narrative
- [ ] Export or screenshot **audit log** showing drift detection, new path, memory save (PRD §9).

### G3. UX pass
- [ ] Loading states (shadcn **Skeleton**), empty states, toast on errors (**Sonner**).
- [ ] Keyboard-accessible controls for mic and send.

---

## Dependency Highlights (Quick Reference)

| Step | Depends on |
|------|------------|
| A4 DB | A3 API shell |
| B2 Playwright | B1 mock app |
| D3 Judge | D2 plan schema |
| D4 Action | B2 bridge + D4 Judge rules |
| D5 Learner | D4 failure contract + B2 |
| E1 widget | C2 or sync message API |
| F1 E2E | All of D*, E* core |

---

## Definition of Done (Prototype)

- [ ] Demo script in PRD §10 runs manually without code changes.
- [ ] At least **one** adaptive memory round-trip visible (store + retrieve on repeat).
- [ ] Audit log shows Router → Knowledge → Judge → Action → (Learner if drift).
- [ ] UI is coherent, minimal, built with **Tailwind + shadcn**.

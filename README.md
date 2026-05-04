# Vani-Flow: Autonomous Resolution Engine

Vani-Flow is a **voice-first, multi-agent autonomous resolution system** built for the Economic Times Gen AI Hackathon. It is designed to not only resolve customer issues end-to-end, but also intelligently adapt to UI and documentation changes, and teach users how to navigate those changes in the future.

## 🚀 Key Features

*   **End-to-End Autonomous Resolution:** Handles repetitive L1 support tickets in under 2 minutes.
*   **Self-Healing UI Agent:** Detects when UI elements change (UI drift), autonomously finds the new correct workflow, and executes it without human intervention.
*   **Dynamic User Guidance:** Teaches non-technical users the new steps when workflows change, reducing repeated tickets.
*   **Structured Auditability:** Maintains a machine-readable audit log for every action taken by the agents.
*   **Voice-First Interface:** Accepts spoken complaints via a web widget.
*   **Local-First Architecture:** Designed to use local Small Language Models (SLMs) to ensure customer data never leaves the company infrastructure.

## 🧠 System Architecture: The 5-Agent Mesh

Vani-Flow utilizes a collaborative mesh of 5 specialized agents:

1.  **Agent 1: Router Agent (The Listener)** - Processes voice/chat input, determines intent, sentiment, and priority.
2.  **Agent 2: Knowledge Agent (The Policy Expert)** - Retrieves relevant company policies and queries the Learning Memory for recent workflow adaptations to create a Resolution Plan.
3.  **Agent 3: Action Agent (The Executor)** - Executes the plan against company systems via APIs or UI automation.
4.  **Agent 4: Judge Agent (The Auditor)** - Validates every proposed action against compliance and safety guardrails before execution, logging all decisions.
5.  **Agent 5: Self-Healing UI Agent (The Learner)** - Triggers upon persistent UI failures to analyze the issue, explore the DOM to find new paths, rebuild the workflow, save it to memory, and generate user guidance.

## 🛠️ Tech Stack

*   **Frontend:** React / Next.js, Tailwind CSS, shadcn/ui
*   **Backend API:** FastAPI (Python)
*   **Orchestration:** LangGraph / Custom Agent Controller
*   **Database:** PostgreSQL (Sessions, Audit Logs)
*   **Vector Store:** ChromaDB / FAISS (RAG and Adaptive Memory)
*   **AI Models:** Local SLMs (e.g., Oumi-fine-tuned), Whisper/Bhashini API for STT

## 🗂️ Project Structure

*   `frontend/` - Contains the React/Next.js UI components (Customer Widget, Ops Dashboard, L2 Escalation View).
*   `backend/` - Contains the FastAPI application, database connections, and API endpoints.
*   `core/` - Core agent logic, orchestrator, and memory management.
*   `DESIGN_VaniFlow.md` - Technical design document and implementation plan for the prototype.
*   `PRD_VaniFlow_v2.md` - Detailed Product Requirements Document.
*   `TODO_PROTOTYPE.md` - Checklist for hackathon prototype development.

## 🎯 The Vani-Flow Difference

> *"Vani-Flow doesn’t just automate workflows—it learns when systems change, adapts in real-time, and even teaches users how to navigate the new interface."*

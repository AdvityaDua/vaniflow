from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import uuid4

from app.schemas.adaptive_memory import AdaptiveMemory
from app.schemas.audit import AuditEntry, JudgeVerdict
from app.schemas.complaint import Complaint, Priority
from app.schemas.session import AgentState, AgentStep


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class SessionRecord:
    session_id: str
    created_at: datetime
    complaint: Optional[Complaint] = None
    steps: List[AgentStep] = field(default_factory=list)


class InMemoryStore:
    def __init__(self) -> None:
        self.sessions: Dict[str, SessionRecord] = {}
        self.audit: List[AuditEntry] = []
        self.adaptive_memory_by_issue: Dict[str, AdaptiveMemory] = {}
        self.drift_mode: str = "off"

    def create_session(self) -> SessionRecord:
        sid = str(uuid4())
        rec = SessionRecord(session_id=sid, created_at=_now())
        self.sessions[sid] = rec
        return rec

    def get_session(self, session_id: str) -> SessionRecord:
        return self.sessions[session_id]

    def append_step(self, session_id: str, agent: str, state: AgentState, summary: str, data: dict) -> AgentStep:
        step = AgentStep(ts=_now(), agent=agent, state=state, summary=summary, data=data)
        self.sessions[session_id].steps.append(step)
        return step

    def append_audit(
        self,
        session_id: str,
        agent: str,
        complaint_id: str | None,
        verdict: JudgeVerdict | None,
        reason: str | None,
        payload: dict,
    ) -> AuditEntry:
        entry = AuditEntry(
            audit_id=str(uuid4()),
            ts=_now(),
            session_id=session_id,
            complaint_id=complaint_id,
            agent=agent,
            verdict=verdict,
            reason=reason,
            payload=payload,
        )
        self.audit.append(entry)
        return entry

    def upsert_adaptive_memory(self, memory: AdaptiveMemory) -> None:
        self.adaptive_memory_by_issue[memory.issue_type] = memory

    def get_adaptive_memory(self, issue_type: str) -> Optional[AdaptiveMemory]:
        return self.adaptive_memory_by_issue.get(issue_type)


store = InMemoryStore()


def basic_router(text: str) -> Complaint:
    t = text.lower()
    intent = "unknown"
    issue_type = "general"
    if "refund" in t or "reimbursement" in t:
        intent = "refund_status"
        issue_type = "refund"

    priority = Priority.routine
    if any(k in t for k in ["urgent", "immediately", "asap", "now"]):
        priority = Priority.urgent
    if any(k in t for k in ["lawsuit", "fraud", "chargeback"]):
        priority = Priority.critical

    complaint_id = f"CMP-{_now().strftime('%Y%m%d')}-{str(uuid4())[:8].upper()}"
    sentiment_score = 0.45 if any(k in t for k in ["angry", "frustrated", "worst", "terrible"]) else 0.6
    return Complaint(complaint_id=complaint_id, intent=intent, priority=priority, sentiment_score=sentiment_score), issue_type


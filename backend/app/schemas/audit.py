from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class JudgeVerdict(str, Enum):
    approved = "approved"
    blocked = "blocked"
    escalate = "escalate"


class AuditEntry(BaseModel):
    audit_id: str
    ts: datetime
    session_id: str
    complaint_id: str | None = None
    agent: str = Field(..., examples=["Router", "Knowledge", "Judge", "Action", "Learner"])
    verdict: JudgeVerdict | None = None
    reason: str | None = None
    payload: dict = Field(default_factory=dict)


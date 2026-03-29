from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.schemas.complaint import Complaint


class AgentState(str, Enum):
    ROUTED = "ROUTED"
    PLANNED = "PLANNED"
    JUDGE_PENDING = "JUDGE_PENDING"
    EXECUTING = "EXECUTING"
    HEALING = "HEALING"
    DONE = "DONE"
    ESCALATED = "ESCALATED"
    FAILED = "FAILED"


class SessionCreateResponse(BaseModel):
    session_id: str
    created_at: datetime


class SessionMessageRequest(BaseModel):
    text: str = Field(..., min_length=1)


class AgentStep(BaseModel):
    ts: datetime
    agent: str
    state: AgentState
    summary: str
    data: Dict[str, Any] = Field(default_factory=dict)


class SessionMessageResponse(BaseModel):
    session_id: str
    complaint: Optional[Complaint] = None
    state: AgentState
    steps: List[AgentStep]
    assistant_message: str
    user_guidance: Optional[str] = None
    adaptive_memory_used: bool = False


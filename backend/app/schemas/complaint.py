from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Priority(str, Enum):
    routine = "routine"
    urgent = "urgent"
    critical = "critical"


class Complaint(BaseModel):
    complaint_id: str = Field(..., examples=["CMP-20260329-00142"])
    intent: str = Field(..., examples=["refund_status"])
    priority: Priority = Field(default=Priority.routine)
    sentiment_score: float = Field(default=0.5, ge=0.0, le=1.0)


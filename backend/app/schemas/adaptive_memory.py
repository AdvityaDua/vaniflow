from __future__ import annotations

from pydantic import BaseModel, Field


class AdaptiveMemory(BaseModel):
    issue_type: str = Field(..., examples=["refund"])
    old_flow: str = Field(..., examples=["Click Dashboard -> Refund"])
    new_flow: str = Field(..., examples=["Click Billing -> Claims -> Process Reimbursement"])
    ui_changes_detected: bool = True
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)


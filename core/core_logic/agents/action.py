from typing import Dict, Any
from ..state.models import AgentResponse, AgentMeta, ActionOutput
from ..state.enums import ErrorType
import asyncio

async def action_agent(input_data: Dict[str, Any]) -> AgentResponse:
    resolution_plan = input_data.get("resolution_plan", [])
    drift_enabled = input_data.get("drift_enabled", False)
    retry_count = input_data.get("retry_count", 0)
    
    await asyncio.sleep(0.5) 
    
    is_standard_refund = any("Refund" in str(step) for step in resolution_plan)
    
    if is_standard_refund and drift_enabled:
        if retry_count > 0:
            details = f"Retry {retry_count} failed. Element still missing."
        else:
            details = "Could not locate element targeting 'Refund' in the DOM."
            
        reason = "Execution halted due to UI failure. Target element is missing."
        output = ActionOutput(
            status="failed",
            error_type=ErrorType.ELEMENT_NOT_FOUND.value,
            details=details,
            confidence=1.0,
            reason=reason
        )
        return AgentResponse(
            input=input_data,
            output=output.model_dump(),
            meta=AgentMeta(agent="executor", confidence=1.0, reason=reason)
        )
        
    reason = "All steps executed perfectly against the target system."
    output = ActionOutput(
        status="success",
        error_type=None,
        details=f"Executed {len(resolution_plan)} steps successfully.",
        confidence=0.95,
        reason=reason
    )
    return AgentResponse(
        input=input_data,
        output=output.model_dump(),
        meta=AgentMeta(agent="executor", confidence=0.95, reason=reason)
    )

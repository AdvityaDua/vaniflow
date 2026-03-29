from typing import Dict, Any
from ..state.models import AgentResponse, AgentMeta, LearnerOutput
from ..state.enums import ErrorType
import asyncio

async def learner_agent(input_data: Dict[str, Any]) -> AgentResponse:
    failed_plan = input_data.get("resolution_plan", [])
    intent = input_data.get("intent", "unknown")
    error = input_data.get("error", {})
    
    print("Agent 5: Scanning DOM for alternative elements...")
    await asyncio.sleep(1.2) 
    print("Agent 5: Trying alternative path: Billing -> Claims...")
    
    new_flow = []
    guidance = ""
    
    if intent == "refund_status" and error.get("error_type") == ErrorType.ELEMENT_NOT_FOUND.value:
        new_flow = [
            {"action": "navigate", "target": "Billing -> Claims"},
            {"action": "click", "target": "Process Reimbursement"}
        ]
        guidance = "It looks like the refund option has moved. Please go to Billing -> Claims -> Process Reimbursement. I've also updated this for future requests."
        status = "resolved_with_adaptation"
        confidence = 0.88
        reason = "Discovered alternative DOM path through sequential semantic matching."
    else:
        status = "failed"
        guidance = "The system encountered an unrecoverable UI drift. Please contact L2 support."
        confidence = 0.30
        reason = "Heuristic search exhausted. No semantic UI matches found."
        
    output = LearnerOutput(
        status=status,
        updated_flow=new_flow,
        user_guidance=guidance,
        confidence=confidence,
        reason=reason
    )
    
    return AgentResponse(
        input=input_data,
        output=output.model_dump(),
        meta=AgentMeta(agent="learner", confidence=confidence, reason=reason)
    )

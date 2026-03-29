from typing import Dict, Any
from ..state.models import AgentResponse, AgentMeta, JudgeOutput
import asyncio

async def judge_agent(input_data: Dict[str, Any]) -> AgentResponse:
    resolution_plan = input_data.get("resolution_plan", [])
    intent = input_data.get("intent", "unknown")
    plan_confidence = input_data.get("plan_confidence", 1.0)
    
    await asyncio.sleep(0.2)
    
    if plan_confidence < 0.6 or not resolution_plan:
        verdict = "escalate"
        reason = "Confidence too low or empty plan. Escalating to human."
        confidence = 0.95
    elif "delete" in str(resolution_plan).lower():
        verdict = "blocked"
        reason = "Plan contains destructive actions. Execution blocked."
        confidence = 0.99
    else:
        verdict = "approved"
        reason = "Plan passes all security checks and standard guidelines."
        confidence = 0.90
        
    output = JudgeOutput(
        verdict=verdict,
        reason=reason,
        confidence=confidence
    )
    
    return AgentResponse(
        input=input_data,
        output=output.model_dump(),
        meta=AgentMeta(agent="judge", confidence=confidence, reason=reason)
    )

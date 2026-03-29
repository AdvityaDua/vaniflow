from typing import Dict, Any
from ..state.models import AgentResponse, AgentMeta, KnowledgeOutput
from ..state.enums import PlanSource
from ..memory.store import get_memory
import asyncio

async def knowledge_agent(input_data: Dict[str, Any]) -> AgentResponse:
    intent = input_data.get("intent", "unknown")
    
    await asyncio.sleep(0.4)
    
    learned_flow = get_memory(intent)
    
    if learned_flow:
        resolution_plan = learned_flow
        source = PlanSource.MEMORY.value
        matched_policies = ["MEMORY: adaptive_flow_retrieved"]
        confidence = 0.98
        reason = "Self-healed workflow found in memory. Reusing exact steps."
    else:
        # Fallback to standard policy
        source = PlanSource.POLICY.value
        if intent == "refund_status":
            resolution_plan = [
                {"action": "navigate", "target": "Dashboard"},
                {"action": "click", "target": "Refund"}
            ]
            matched_policies = ["POLICY: POL-01-REFUNDS"]
            confidence = 0.85
            reason = "Standard refund policy retrieved from static KB."
        else:
            resolution_plan = []
            matched_policies = ["POLICY: DEFAULT"]
            confidence = 0.50
            reason = "No specific policy matched. Using empty default plan."
            
    output = KnowledgeOutput(
        resolution_plan=resolution_plan,
        source=source,
        matched_policies=matched_policies,
        confidence=confidence,
        reason=reason
    )
    
    return AgentResponse(
        input=input_data,
        output=output.model_dump(),
        meta=AgentMeta(agent="knowledge", confidence=confidence, reason=reason)
    )

import os
from typing import Dict, Any
from ..state.models import AgentResponse, AgentMeta, RouterOutput
from dotenv import load_dotenv
import asyncio

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

async def router_agent(input_data: Dict[str, Any]) -> AgentResponse:
    text = input_data.get("text", "")
    
    # 2. Integrate Gemini for natural conversation while strictly enforcing JSON Output
    if GEMINI_API_KEY:
        from google import genai
        from google.genai import types
        import json
        
        # We explicitly wrap the LLM call to never leak unformatted strings into the orchestrator
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # LangGraph runs async, so we use thread-blocking call or async call if supported.
        # google-genai supports async client via `client.aio.models.generate_content`
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Analyze this customer complaint and extract intent and priority concisely: '{text}'",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                # Force Gemini to strictly output following our RouterOutput format
                response_schema=RouterOutput,
                temperature=0.1,
                system_instruction=(
                    "You are the Router Agent. "
                    "Classify enterprise complaints. "
                    "Determine intent (e.g. 'refund_status', 'billing_issue', 'technical_support'). "
                    "Determine category, and set a priority string ('low', 'medium', 'high'). "
                    "Return a short 'reason' describing why you made this classification. "
                    "Return confidence as a float between 0.0 and 1.0."
                )
            ),
        )
        
        result_dict = json.loads(response.text)
        
        output = RouterOutput(
            intent=result_dict.get("intent", "general_inquiry"),
            confidence=float(result_dict.get("confidence", 0.9)),
            category=result_dict.get("category", "general"),
            priority=result_dict.get("priority", "low"),
            reason=result_dict.get("reason", "Analyzed via Gemini.")
        )
    else:
        # Graceful deterministic fallback
        await asyncio.sleep(0.3) 
        if "refund" in text.lower() or "reimbursement" in text.lower():
            output = RouterOutput(
                intent="refund_status", confidence=0.92, category="billing", priority="high",
                reason="Keywords 'refund'/'reimbursement' detected strongly."
            )
        else:
            output = RouterOutput(
                intent="general_inquiry", confidence=0.85, category="general", priority="low",
                reason="No specific high-priority keywords found. Defaulting to general."
            )
            
    return AgentResponse(
        input=input_data,
        output=output.model_dump(),
        meta=AgentMeta(agent="router", confidence=output.confidence, reason=output.reason)
    )

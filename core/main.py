import uuid
import json
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from core_logic.orchestrator.graph import app_orchestrator

app = FastAPI(title="Vani-Flow Orchestrator API")

class MessageRequest(BaseModel):
    text: str
    drift_enabled: bool = False

@app.post("/sessions/{session_id}/message")
async def send_message(session_id: str, request: MessageRequest):
    initial_state = {
        "core": {
            "session_id": session_id,
            "status": "INITIAL",
            "retry_count": 0,
            "max_retries": 1,
            "run_type": "cold",
            "latency_map": {}
        },
        "data": {
            "input_text": request.text,
            "complaint_id": f"CMP-{uuid.uuid4().hex[:6].upper()}",
            "intent": None,
            "confidence": None,
            "resolution_plan": [],
            "source": None
        },
        "execution": {
            "current_error": None,
            "action_results": [],
            "final_guidance": None,
            "drift_enabled": request.drift_enabled,
            "drift_detected": False,
            "escalation_payload": None
        },
        "execution_path": [],
        "audit_log": []
    }

    async def event_stream():
        step_counter = 1
        current_state = initial_state
        
        async for output in app_orchestrator.astream(initial_state):
            for node_name, state_update in output.items():
                
                # Merge patches to maintain final state accurately
                for key, val in state_update.items():
                    if isinstance(val, dict) and key in current_state:
                        current_state[key].update(val)
                    else:
                        current_state[key] = val
                
                if node_name.startswith("done_"):
                    continue
                    
                audit = state_update.get("audit_log", [])
                latest_audit = audit[-1] if audit else {}
                
                # 3. Reasoning String per Agent implemented
                msg = latest_audit.get("reason") or "Executed step"
                
                event_data = {
                    "event": "AGENT_STEP",
                    "step_id": step_counter,
                    "agent": latest_audit.get("agent", node_name),
                    "status": latest_audit.get("status", "processing"),
                    "latency_ms": latest_audit.get("latency_ms", 0),
                    "message": msg
                }
                
                yield f"data: {json.dumps(event_data)}\n\n"
                step_counter += 1
                
        # 2.1 Final Output Contract
        final_status = current_state["core"].get("status", "COMPLETED").lower()
        if final_status == "done":
            final_status = "success"
            
        final_payload = {
            "event": "FINAL_RESPONSE",
            "status": final_status,
            "message": "Resolution workflow completed." if final_status == "success" else "Workflow halted.",
            "guidance": current_state["execution"].get("final_guidance"),
            "execution_path": current_state.get("execution_path", []),
            "source": current_state["data"].get("source", "unknown"),
            "run_type": current_state["core"].get("run_type", "cold"),
            "latency_map": current_state["core"].get("latency_map", {}),
            "escalation_payload": current_state["execution"].get("escalation_payload"),
            "drift_detected": current_state["execution"].get("drift_detected", False)
        }
        
        yield f"data: {json.dumps(final_payload)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

import time
from langgraph.graph import StateGraph, END
from ..state.models import ProcessState
from ..state.enums import StateStatus, ErrorType
from ..utils.logger import create_audit_entry
from ..memory.store import save_memory

from ..agents.router import router_agent
from ..agents.knowledge import knowledge_agent
from ..agents.judge import judge_agent
from ..agents.action import action_agent
from ..agents.learner import learner_agent

# --- LANGGRAPH NODE WRAPPERS ---

async def node_router(state: ProcessState) -> dict:
    start_time = time.time()
    resp = await router_agent({"text": state["data"]["input_text"]})
    out = resp.output
    latency = int((time.time() - start_time) * 1000)
    
    return {
        "core": {**state["core"], "status": StateStatus.ROUTED.value, "latency_map": {**state["core"].get("latency_map", {}), "router": latency}},
        "data": {**state["data"], "intent": out["intent"], "confidence": out["confidence"]},
        "execution_path": state.get("execution_path", []) + ["router"],
        "audit_log": state["audit_log"] + [create_audit_entry("router", "classify_intent", "success", out["reason"], latency)]
    }

async def node_knowledge(state: ProcessState) -> dict:
    start_time = time.time()
    resp = await knowledge_agent({"intent": state["data"]["intent"]})
    out = resp.output
    latency = int((time.time() - start_time) * 1000)
    
    # Toggle explicit run_type flag
    run_type = "learned" if out["source"] == "memory" else "cold"
    
    return {
        "core": {
            **state["core"], 
            "status": StateStatus.PLANNED.value, 
            "latency_map": {**state["core"].get("latency_map", {}), "knowledge": latency},
            "run_type": run_type
        },
        "data": {**state["data"], "resolution_plan": out["resolution_plan"], "source": out["source"]},
        "execution_path": state.get("execution_path", []) + ["knowledge"],
        "audit_log": state["audit_log"] + [create_audit_entry(
            "knowledge", "plan_generation", "success", out['reason'], latency
        )]
    }

async def node_judge(state: ProcessState) -> dict:
    start_time = time.time()
    resp = await judge_agent({
        "intent": state["data"]["intent"], 
        "resolution_plan": state["data"]["resolution_plan"],
        "plan_confidence": state["data"].get("confidence", 1.0)
    })
    out = resp.output
    latency = int((time.time() - start_time) * 1000)
    
    overall_status = StateStatus.JUDGE_PENDING.value
    escalation_payload = None
    if out["confidence"] < 0.6 or out["verdict"] != "approved":
        overall_status = StateStatus.ESCALATED.value
        out["verdict"] = "escalate"
        
        # 2.2 Human Escalation Payload
        escalation_payload = {
            "reason": out["reason"],
            "recovery_plan": str(state["data"]["resolution_plan"]),
            "audit_summary": f"Escalated by Judge after {len(state['audit_log'])} successful upstream steps."
        }
    
    return {
        "core": {**state["core"], "status": overall_status, "latency_map": {**state["core"].get("latency_map", {}), "judge": latency}},
        "execution": {**state["execution"], "escalation_payload": escalation_payload},
        "execution_path": state.get("execution_path", []) + ["judge"],
        "audit_log": state["audit_log"] + [create_audit_entry("judge", "validate_plan", out["verdict"], out["reason"], latency)]
    }

async def node_action(state: ProcessState) -> dict:
    start_time = time.time()
    resp = await action_agent({
        "resolution_plan": state["data"]["resolution_plan"], 
        "drift_enabled": state["execution"]["drift_enabled"],
        "retry_count": state["core"]["retry_count"]
    })
    out = resp.output
    latency = int((time.time() - start_time) * 1000)
    
    new_retry = state["core"]["retry_count"]
    drift_detected = state["execution"].get("drift_detected", False)
    
    if out["status"] == "failed":
        new_retry += 1
        if out["error_type"] == ErrorType.ELEMENT_NOT_FOUND.value:
            drift_detected = True  # 2.3 Explicit Drift Signal
        
    return {
        "core": {**state["core"], "status": StateStatus.EXECUTING.value, "retry_count": new_retry, "latency_map": {**state["core"].get("latency_map", {}), "action": latency}},
        "execution": {
            **state["execution"],
            "current_error": {"error_type": out["error_type"], "details": out["details"]} if out["status"] == "failed" else None,
            "drift_detected": drift_detected
        },
        "execution_path": state.get("execution_path", []) + ["action"],
        "audit_log": state["audit_log"] + [create_audit_entry("action", "execute_ui", out["status"], out["reason"], latency)]
    }

async def node_learner(state: ProcessState) -> dict:
    start_time = time.time()
    resp = await learner_agent({
        "error": state["execution"]["current_error"],
        "intent": state["data"]["intent"],
        "resolution_plan": state["data"]["resolution_plan"]
    })
    out = resp.output
    latency = int((time.time() - start_time) * 1000)
    
    if out["status"] == "resolved_with_adaptation":
        save_memory(state["data"]["intent"], out["updated_flow"])
    
    return {
        "core": {**state["core"], "status": StateStatus.HEALING.value, "latency_map": {**state["core"].get("latency_map", {}), "learner": latency}},
        "execution": {**state["execution"], "final_guidance": out["user_guidance"]},
        "execution_path": state.get("execution_path", []) + ["learner"],
        "audit_log": state["audit_log"] + [create_audit_entry("learner", "self_heal", out["status"], out["reason"], latency)]
    }

# --- EDGE CONDITIONS ---
def edge_after_judge(state: ProcessState) -> str:
    log = state["audit_log"][-1] if state["audit_log"] else {}
    if log.get("status") == "approved":
        return "action"
    return "done_escalated"

def edge_after_action(state: ProcessState) -> str:
    err = state["execution"].get("current_error")
    retries = state["core"]["retry_count"]
    max_retries = state["core"]["max_retries"]
    
    if err and err.get("error_type") == ErrorType.ELEMENT_NOT_FOUND.value:
        if retries < max_retries:
            print(f"Action failed. Retrying... ({retries}/{max_retries})")
            return "action" 
        else:
            return "learner" 
    elif err:
        return "done_failed"
    return "done_success"

def build_orchestrator() -> StateGraph:
    workflow = StateGraph(ProcessState)
    workflow.add_node("router", node_router)
    workflow.add_node("knowledge", node_knowledge)
    workflow.add_node("judge", node_judge)
    workflow.add_node("action", node_action)
    workflow.add_node("learner", node_learner)

    def set_done(state: ProcessState): return {"core": {**state["core"], "status": StateStatus.DONE.value}}
    def set_escalated(state: ProcessState): return {"core": {**state["core"], "status": StateStatus.ESCALATED.value}}
    def set_failed(state: ProcessState): return {"core": {**state["core"], "status": StateStatus.FAILED.value}}
    
    workflow.add_node("done_success", set_done)
    workflow.add_node("done_escalated", set_escalated)
    workflow.add_node("done_failed", set_failed)

    workflow.set_entry_point("router")
    workflow.add_edge("router", "knowledge")
    workflow.add_edge("knowledge", "judge")
    
    workflow.add_conditional_edges("judge", edge_after_judge, {"action": "action", "done_escalated": "done_escalated"})
    workflow.add_conditional_edges("action", edge_after_action, {"action": "action", "learner": "learner", "done_success": "done_success", "done_failed": "done_failed"})
    
    workflow.add_edge("learner", "done_success")
    workflow.add_edge("done_success", END)
    workflow.add_edge("done_escalated", END)
    workflow.add_edge("done_failed", END)
    
    return workflow.compile()

app_orchestrator = build_orchestrator()

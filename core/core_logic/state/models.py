from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
import datetime

# --- Pydantic IO Contracts for Pure Functions ---
class AgentMeta(BaseModel):
    agent: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    confidence: float = 1.0
    reason: str = "" # Added universal reasoning string

class AgentResponse(BaseModel):
    input: Dict[str, Any]
    output: Dict[str, Any]
    meta: AgentMeta

# --- Final Frontend Contract ---
class FinalResponse(BaseModel):
    status: str # "success | failed | escalated"
    message: str 
    guidance: Optional[str]
    execution_path: List[str]
    source: Optional[str]
    run_type: Optional[str]
    latency_map: Dict[str, int]
    escalation_payload: Optional[Dict[str, Any]]

# --- LangGraph State Schema (Nested to avoid bloat) ---
class CoreState(TypedDict):
    session_id: str
    status: str
    retry_count: int
    max_retries: int
    run_type: Optional[str] # "cold" or "learned"
    latency_map: Dict[str, int]

class DataState(TypedDict):
    input_text: str
    complaint_id: Optional[str]
    intent: Optional[str]
    confidence: Optional[float]
    resolution_plan: Optional[List[Dict[str, Any]]]
    source: Optional[str]  # "memory" or "policy"

class ExecutionState(TypedDict):
    current_error: Optional[Dict[str, Any]]
    action_results: List[Dict[str, Any]]
    final_guidance: Optional[str]
    drift_enabled: bool 
    drift_detected: bool # Explicit telemetry
    escalation_payload: Optional[Dict[str, Any]] # "reason", "recovery_plan", "audit_summary"

class ProcessState(TypedDict):
    core: CoreState
    data: DataState
    execution: ExecutionState
    execution_path: List[str]
    audit_log: List[Dict[str, Any]]

# --- Specific Agent Output Dictionaries ---
class RouterOutput(BaseModel):
    intent: str
    category: str
    priority: str
    confidence: float
    reason: str

class KnowledgeOutput(BaseModel):
    resolution_plan: List[Dict[str, Any]]
    source: str
    matched_policies: List[str]
    confidence: float
    reason: str

class JudgeOutput(BaseModel):
    verdict: str  # "approved", "blocked", "escalate"
    reason: str
    confidence: float

class ActionOutput(BaseModel):
    status: str
    error_type: Optional[str] = None
    details: Optional[str] = None
    confidence: float
    reason: str

class LearnerOutput(BaseModel):
    status: str
    updated_flow: Optional[List[Dict[str, Any]]] = None
    user_guidance: Optional[str] = None
    confidence: float
    reason: str

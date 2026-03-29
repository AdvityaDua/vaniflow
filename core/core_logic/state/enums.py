from enum import Enum

class StateStatus(str, Enum):
    INITIAL = "INITIAL"
    ROUTED = "ROUTED"
    PLANNED = "PLANNED"
    JUDGE_PENDING = "JUDGE_PENDING"
    EXECUTING = "EXECUTING"
    HEALING = "HEALING"
    DONE = "DONE"
    ESCALATED = "ESCALATED"
    FAILED = "FAILED"

class ErrorType(str, Enum):
    ELEMENT_NOT_FOUND = "ELEMENT_NOT_FOUND"
    API_FAILURE = "API_FAILURE"
    TIMEOUT = "TIMEOUT"
    UNKNOWN = "UNKNOWN"

class PlanSource(str, Enum):
    POLICY = "policy"
    MEMORY = "memory"

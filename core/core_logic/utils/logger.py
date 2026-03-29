import datetime
from typing import Dict, Any

def create_audit_entry(agent: str, step: str, status: str, reason: str = "", latency_ms: int = 0) -> Dict[str, Any]:
    """
    3.2 Audit Log Should Be QUERYABLE
    Structure ensuring ops dashboards can query performance and verdicts.
    """
    return {
        "agent": agent,
        "step": step,
        "status": status,
        "reason": reason,
        "timestamp": datetime.datetime.now().isoformat(),
        "latency_ms": latency_ms
    }

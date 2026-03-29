from typing import List, Dict, Any, Optional

# Private mock store
_MOCK_LEARNING_MEMORY: Dict[str, List[Dict[str, Any]]] = {}

def get_memory(issue_type: str) -> Optional[List[Dict[str, Any]]]:
    """Retrieve an adapted flow for an issue type if it exists."""
    return _MOCK_LEARNING_MEMORY.get(issue_type)

def save_memory(issue_type: str, flow: List[Dict[str, Any]]) -> None:
    """Save a newly learned flow to the memory store."""
    if issue_type and flow:
        _MOCK_LEARNING_MEMORY[issue_type] = flow

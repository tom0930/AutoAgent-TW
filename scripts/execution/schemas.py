from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class ExecutionNode(BaseModel):
    """
    Represents a single atomic execution task inside the multi-agent DAG.
    """
    id: str
    role: str
    files: List[str] = Field(default_factory=list)
    depends_on: List[str] = Field(default_factory=list)
    adopted_decision: Optional[str] = None
    
    model_config = ConfigDict(frozen=True)

class TaskResult(BaseModel):
    """
    Represents the output result of an executed node.
    """
    task_id: str
    success: bool
    diff_hash: Optional[str] = None
    exit_code: int = 0
    token_used: int = 0
    error_message: Optional[str] = None

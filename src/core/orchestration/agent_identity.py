import enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AgentRole(str, enum.Enum):
    COORDINATOR = "coordinator"
    META_COORDINATOR = "meta_coordinator"
    CODER = "coder"
    TESTER = "tester"
    REVIEWER = "reviewer"
    OMNISCIENT = "omniscient"

class TrustLevel(int, enum.Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    ADMIN = 4

class CapabilityCard(BaseModel):
    """
    Agent Identity Card (Phase 171 v2.1)
    Defines who the agent is and what it is allowed to do.
    """
    agent_id: str = Field(..., description="Unique UUID for the agent session")
    role: AgentRole
    trust_level: TrustLevel
    allowed_tools: List[str] = Field(default_factory=list)
    forbidden_tools: List[str] = Field(default_factory=list)
    
    # Resource & Cost Control
    model_preference: str = "flash"
    max_tokens_per_task: int = 8000
    max_memory_mb: int = 256
    ttl_seconds: int = 300
    
    # Learning & Feedback
    learning_rate: float = 0.1
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True

import operator
from typing import TypedDict, Annotated, List, Dict, Optional, Any
from langchain_core.messages import BaseMessage

# IRA 5-Level Permission Agent State Definition (Phase 120 - Wave 1)
class AgentState(TypedDict):
    """
    Expanded Agent State for LangGraph Orchestration with a dynamic 
    5-level tool permission guard (IRA requirement).
    """
    # Core Communication
    messages: Annotated[List[BaseMessage], operator.add]
    task_input: str
    
    # Versioning & Resilience (Legacy from PISRC Phase 119)
    failure_count: int
    last_errors: List[str]
    current_version: str
    
    # IRA Permission & Risk Control Fields (New in Phase 120)
    # Risk Level mapping: 5(Fatal), 4(High), 3(Medium), 2(Low), 1(Read)
    risk_level: int
    last_action: Optional[Dict[str, Any]]
    pending_approval: bool
    approval_result: Optional[str]        # 'approved', 'denied', or 'modified'
    
    # MCP Tool Orchestration (Phase 125 Wave 2)
    mcp_tools_used: List[str]
    tool_outputs: List[Dict[str, Any]]
    tool_errors: List[str]
    # Context & Persistence
    thread_id: str
    review_reports: List[Dict]
    success_rate: float

import os
from typing import TypedDict, Annotated, List, Dict, Optional, Any
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig

# Load env for LangSmith
load_dotenv()

# pyrefly: ignore [missing-import]
from src.core.state import AgentState
# pyrefly: ignore [missing-import]
from src.core.permission_engine import PermissionEngine
# pyrefly: ignore [missing-import]
from src.core.persistence import get_checkpointer

# Setup Engine
permission_engine = PermissionEngine()

def gatekeeper_node(state: AgentState, config: RunnableConfig):
    """
    IRA 5-Level Permission Guard Node (Phase 120 - Task 2.2 / 3.2).
    Includes LangSmith tagging for observability.
    """
    last_action = state.get("last_action")
    if not last_action:
        return {"pending_approval": False}
    
    tool_name = last_action.get("name", "unknown")
    risk = permission_engine.get_risk_level(tool_name)
    
    # Update risk level in state
    state["risk_level"] = risk
    
    # Determine if we interrupt
    is_trusted = False 
    should_stop, reason = permission_engine.should_interrupt(tool_name, is_trusted)
    
    # LangSmith Tracing (Wave 3B)
    decision = "interrupt" if should_stop else "auto-execute"
    config["tags"] = config.get("tags", []) + ["ira_guard"]
    config["metadata"] = {
        **config.get("metadata", {}),
        "permission_level": risk,
        "decision": decision,
        "tool_name": tool_name
    }
    
    if should_stop:
        return {
            "pending_approval": True,
            "risk_level": risk,
            "messages": [AIMessage(content=f"PERMISSION BLOCK: {reason} Waiting for manual approval.")]
        }
        
    return {"pending_approval": False, "risk_level": risk}

def tool_executor_node(state: AgentState):
    """Mock Tool Executor for Phase 120 testing."""
    last_action = state.get("last_action")
    return {
        "messages": [AIMessage(content=f"Tool '{last_action.get('name')}' executed successfully.")],
        "last_action": None,
        "pending_approval": False
    }

def compile_ira_graph(db_path: str = "checkpoints.sqlite"):
    """
    Compiles the IRA 5-Level Permission Graph with SqliteSaver persistence.
    """
    checkpointer = get_checkpointer(db_path)
    workflow = StateGraph(AgentState)
    
    workflow.add_node("gatekeeper", gatekeeper_node)
    workflow.add_node("tool_executor", tool_executor_node)
    
    # Edge logic
    workflow.add_edge(START, "gatekeeper")
    
    # Conditional jump: Only execute tool if not pending approval
    workflow.add_conditional_edges(
        "gatekeeper",
        lambda x: "tool_executor" if not x.get("pending_approval") else "__end__",
        {
            "tool_executor": "tool_executor",
            "__end__": END
        }
    )
    
    workflow.add_edge("tool_executor", END)
    
    # Interrupt before gatekeeper to allow manual intervention if needed
    # (Actually the plan says 'Logic: Risk >= 4 -> trigger_interrupt()')
    # In LangGraph, we use interrupt_before when pending_approval is True
    app = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["tool_executor"] if [ # This is tricky since it's dynamic
            # In a real app, you might interrupt 'gatekeeper' if you want to modify state 
            # or 'tool_executor' if you want to block the call.
        ] else []
    )
    
    return app

if __name__ == "__main__":
    print("Initializing IRA 5-Level Permission Graph...")
    app = compile_ira_graph("temp/ira_persistence.sqlite")
    print("IRA Graph Compiled with SQLite Persistence (1A/2AB).")
    
    # Test execution simulation
    test_state = {
        "messages": [],
        "task_input": "Delete the main production database",
        "last_action": {"name": "delete_database", "args": {}},
        "failure_count": 0,
        "last_errors": [],
        "current_version": "v1.0",
        "risk_level": 1, 
        "pending_approval": False,
        "approval_result": None,
        "thread_id": "test-ira-001",
        "review_reports": [],
        "success_rate": 0.0
    }
    
    config = {"configurable": {"thread_id": "test-ira-001"}}
    
    print("\n--- Running Test Case: delete_database (Risk 5) ---")
    for event in app.stream(test_state, config=config):
        print(event)
    
    # Check if we are stuck at gatekeeper
    snapshot = app.get_state(config)
    print(f"\nCurrent State Node: {snapshot.next}")
    print(f"Pending Approval: {snapshot.values.get('pending_approval')}")

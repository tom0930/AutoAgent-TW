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
from src.core.mcp.contract_engine import ContractEngine
# pyrefly: ignore [missing-import]
from src.core.persistence import get_checkpointer

# Setup Engine
permission_engine = PermissionEngine()
CONTRACT_LOG_PATH = "z:/autoagent-TW/.planning/phases/153-hitl-contracts/signed_contracts.jsonl"

def log_contract(contract: Dict[str, Any]):
    """Appends the signed contract to a local JSONL file for non-repudiation."""
    import json
    os.makedirs(os.path.dirname(CONTRACT_LOG_PATH), exist_ok=True)
    with open(CONTRACT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(contract) + "\n")

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
        # Phase 153: Generate high-fidelity verification contract
        thread_id = config["configurable"].get("thread_id", "anonymous")
        args = last_action.get("args", {})
        
        contract = ContractEngine.generate_contract(
            thread_id=thread_id,
            risk_level=risk,
            tool_name=tool_name,
            args=args
        )
        
        # Phase 153: Persist for non-repudiation audit
        log_contract(contract)
        
        return {
            "pending_approval": True,
            "risk_level": risk,
            "verification_contract": contract,
            "messages": [AIMessage(content=f"PERMISSION BLOCK: {reason}\n\n[Verification Contract v1.0 Generated]\nHash: {contract['hash']}\nPlease type 'approve' to proceed.")]
        }
        
    return {"pending_approval": False, "risk_level": risk, "verification_contract": None}

def tool_executor_node(state: AgentState):
    """Mock Tool Executor with Phase 153 Hash Verification."""
    last_action = state.get("last_action")
    contract = state.get("verification_contract")
    
    # Phase 153: Strict drift protection
    if contract:
        current_args = last_action.get("args", {})
        if not ContractEngine.verify_contract(contract, current_args):
            return {
                "messages": [AIMessage(content="CRITICAL: Verification Failure! Tool arguments have changed since approval (Agent Drift detected). Execution blocked.")],
                "tool_errors": ["Contract Hash Mismatch"],
                "pending_approval": False
            }
            
    return {
        "messages": [AIMessage(content=f"Tool '{last_action.get('name')}' executed successfully with valid contract signature.")],
        "last_action": None,
        "pending_approval": False,
        "verification_contract": None # Clear contract after success
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
        "task_input": "Execute a high-risk system command",
        "last_action": {"name": "run_command", "args": {"command": "rm -rf /"}}, # Level 4
        "failure_count": 0,
        "last_errors": [],
        "current_version": "v1.0",
        "risk_level": 1, 
        "pending_approval": False,
        "approval_result": None,
        "verification_contract": None,
        "thread_id": "test-p153-001",
        "review_reports": [],
        "success_rate": 0.0,
        "mcp_tools_used": [],
        "tool_outputs": [],
        "tool_errors": []
    }
    
    config = {"configurable": {"thread_id": "test-ira-001"}}
    
    print("\n--- Running Test Case: delete_database (Risk 5) ---")
    for event in app.stream(test_state, config=config):
        print(event)
    
    # Check if we are stuck at gatekeeper
    snapshot = app.get_state(config)
    print(f"\nCurrent State Node: {snapshot.next}")
    print(f"Pending Approval: {snapshot.values.get('pending_approval')}")

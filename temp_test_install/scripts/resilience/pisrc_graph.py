import operator
from typing import TypedDict, Annotated, List, Dict, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# PISRC Agent State Definition (Wave 2)
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    task_input: str
    failure_count: int
    issue_category: str
    last_errors: List[str]
    current_version: str
    proposed_fix: Optional[Dict]
    review_reports: List[Dict]
    success_rate: float
    thread_id: str

# PISRC Node Implementations (Wave 3)
def task_executor(state: AgentState):
    """
    Mock Executor: To be wired up to actual AutoAgent run execution.
    For PISRC testing, it simulates failures if failure_count < 3.
    """
    new_failure_count = state.get("failure_count", 0) + 1
    error_msg = f"Simulated failure #{new_failure_count}"
    
    return {
        "messages": [AIMessage(content=error_msg)],
        "failure_count": new_failure_count,
        "last_errors": state.get("last_errors", []) + [error_msg]
    }

def issue_detector(state: AgentState):
    """Gatekeeper to detect if task failed persistently (> N times)."""
    # END is a string constant from langgraph.graph, imported explicitly below
    if state.get("failure_count", 0) >= 3:
        return "level1_reviewer"
    return "__end__"

def level1_reviewer(state: AgentState):
    """
    Level 1 Reviewer Node:
    Performs a shallow heuristic evaluation of the accumulated errors.
    It identifies superficial patterns and suggests immediate, easy-to-apply fixes (e.g., prompt tweaks).
    """
    report = {
        "level": 1,
        "content": f"Heuristic Analysis of errors: {state.get('last_errors', [])[-3:]}. Recommend simple prompt tweak."
    }
    return {
        "review_reports": state.get("review_reports", []) + [report],
        "proposed_fix": {"type": "prompt", "content": "Adjust prompt explicitly avoiding known traps."}
    }

def level2_analyzer(state: AgentState):
    """
    Level 2 Analyzer Node (RCA):
    Performs a deep Root Cause Analysis using a '5 Whys' approach.
    It looks beyond symptoms to identify underlying logic or architectural fails.
    """
    report = {
        "level": 2,
        "content": f"5 Whys RCA on errors. Root cause identified: State pollution."
    }
    return {
        "review_reports": state.get("review_reports", []) + [report],
        "proposed_fix": {"type": "memory", "content": "Clear conflicting memory variables."}
    }

def corrector(state: AgentState):
    """
    Corrector Node:
    Actualizes the proposed fixes from the review phase. 
    It increments the versioning and clears the failure counter to restart the task loop.
    """
    fix = state.get("proposed_fix")
    content = fix["content"] if fix else "No fix applied"
    new_version = f"v{state.get('failure_count', 0)}.1"
    
    return {
        "current_version": new_version,
        "failure_count": 0, # Reset after fix
        "messages": [AIMessage(content=f"Applied Fix: {content} -> Now running {new_version}")]
    }

def validator(state: AgentState):
    """
    Validator Node:
    Assesses the stability of the new 'corrected' version.
    In a real scenario, this would run a suite of regression tests.
    """
    simulated_success = 0.90 # Simulate a 90% success rate on the new version
    return {
        "success_rate": simulated_success
    }

def validator_router(state: AgentState):
    if state.get("success_rate", 0) > 0.8:
        return "__end__"
    return "human_interrupt"

def human_interrupt(state: AgentState):
    """Human-in-the-Loop breakpoint."""
    return {"messages": [AIMessage(content="PISRC halted. Fix unsuccessful. Waiting for human intervention.")]}

# Graph Compilation Setup
def compile_pisrc_graph(memory_saver):
    from langgraph.graph import StateGraph, START, END
    
    workflow = StateGraph(AgentState)
    
    workflow.add_node("task_executor", task_executor)
    # issue_detector is a conditional edge router, not a node
    workflow.add_node("level1_reviewer", level1_reviewer)
    workflow.add_node("level2_analyzer", level2_analyzer)
    workflow.add_node("corrector", corrector)
    workflow.add_node("validator", validator)
    workflow.add_node("human_interrupt", human_interrupt)

    # Edge connections
    workflow.add_edge(START, "task_executor")
    
    workflow.add_conditional_edges(
        "task_executor",
        issue_detector,
        {
            "level1_reviewer": "level1_reviewer",
            "__end__": END
        }
    )
    
    # Reviewer pipeline
    workflow.add_edge("level1_reviewer", "level2_analyzer")
    workflow.add_edge("level2_analyzer", "corrector")
    workflow.add_edge("corrector", "validator")
    
    workflow.add_conditional_edges(
        "validator",
        validator_router,
        {
            "__end__": END,
            "human_interrupt": "human_interrupt"
        }
    )
    
    # Human intervention ends the automated graph run context
    workflow.add_edge("human_interrupt", END)
    
    app = workflow.compile(
        checkpointer=memory_saver,
        interrupt_before=["human_interrupt"]
    )
    
    return app

if __name__ == "__main__":
    from langgraph.checkpoint.memory import MemorySaver
    
    print("Testing PISRC Component Graph Compilation...")
    memory = MemorySaver() # Using MemorySaver for easy standalone test
    app = compile_pisrc_graph(memory)
    
    test_state = {
        "task_input": "Deploy testing environment",
        "messages": [],
        "failure_count": 2, # Setting to 2 so execution pushes it to 3 -> triggers reviewer
        "last_errors": ["Error 1", "Error 2"],
        "current_version": "v1.0"
    }
    
    config = {"configurable": {"thread_id": "test-pisrc-001"}}
    
    for chunk in app.stream(test_state, config=config, stream_mode="updates"):
        print(chunk)

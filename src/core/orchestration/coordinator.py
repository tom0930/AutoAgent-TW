import os
import json
import uuid
import asyncio
from typing import List, Dict, Any, Annotated, Union
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from src.core.state import AgentState
from src.core.orchestration.spawn_manager import AgentProcess

class OrchestrationCoordinator:
    """
    Main coordinator for Phase 124 Sub-Agent Engine.
    Uses LangGraph to manage task splitting and parallel execution via process isolation.
    """
    def __init__(self, thread_id: str = "orchestrator-001"):
        self.thread_id = thread_id
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        builder = StateGraph(AgentState)
        
        # Nodes
        builder.add_node("supervisor", self.supervisor_node)
        builder.add_node("execute_tasks", self.execute_tasks_node)
        builder.add_node("aggregator", self.aggregator_node)
        
        # Edges
        builder.add_edge(START, "supervisor")
        builder.add_edge("supervisor", "execute_tasks")
        builder.add_edge("execute_tasks", "aggregator")
        builder.add_edge("aggregator", END)
        
        return builder.compile()

    async def supervisor_node(self, state: AgentState) -> Dict[str, Any]:
        """Splits high-level task into parallelizable sub-tasks."""
        task_input = state["task_input"]
        # In a real scenario, call LLM to split. Here we use an improved heuristic/mock.
        # Goal: Split prompt by 'and' or '.' basic logic for testing.
        tasks = []
        if " and " in task_input:
            tasks = [t.strip() for t in task_input.split(" and ")]
        else:
            tasks = [task_input]
            
        return {
            "messages": [AIMessage(content=f"Supervisor split task into {len(tasks)} sub-tasks.")],
            "pending_approval": False, # Future IRD check
            "last_action": {"tasks": tasks} # Use dict for passing tasks to next node
        }

    async def execute_tasks_node(self, state: AgentState) -> Dict[str, Any]:
        """Spawns processes for each identified task in parallel."""
        tasks = state.get("last_action", {}).get("tasks", [])
        processes = []
        
        for task in tasks:
            print(f"[*] Spawning sub-agent for task: {task}")
            p = AgentProcess(task_name=task, parent_id=self.thread_id)
            # Spawn a simple echo agent for Phase 1 testing
            # In v1.9.0 production, this command would be 'python scripts/aa_agent.py --task ...'
            p.spawn([sys_executable(), "-c", f"import time; print('Starting {task}'); time.sleep(5); print('Done {task}')"])
            processes.append(p)
            
        # Poll for completion (non-blocking simulation)
        # Note: In future waves, we'll implement wait_all in spawn_manager
        results = []
        for p in processes:
            # Simple sync wait for Wave 2 logic
            if p.process:
                p.process.wait()
                p.update_progress(100, f"Task '{task}' completed successfully.")
                results.append(f"Task '{p.task_name}': DONE (ID: {p.agent_id})")
        
        return {
            "messages": [AIMessage(content="\n".join(results))],
            "review_reports": [{"agent_id": p.agent_id, "task": p.task_name} for p in processes]
        }

    async def aggregator_node(self, state: AgentState) -> Dict[str, Any]:
        """Finalizes the orchestration run."""
        return {
            "messages": [AIMessage(content="Final aggregation complete. All sub-agents synced.")],
            "success_rate": 1.0
        }

    def run(self, task_prompt: str):
        """Entry point for orchestration."""
        initial_state = {
            "messages": [],
            "task_input": task_prompt,
            "failure_count": 0,
            "last_errors": [],
            "current_version": "v1.9.0",
            "risk_level": 1,
            "pending_approval": False,
            "approval_result": None,
            "thread_id": self.thread_id,
            "review_reports": [],
            "success_rate": 0.0
        }
        # Execute asynchronously as coordinator.run is sync wrapper
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.graph.ainvoke(initial_state))

def sys_executable():
    import sys
    return sys.executable

if __name__ == "__main__":
    orchestrator = OrchestrationCoordinator()
    print("Running parallel orchestration test...")
    orchestrator.run("Create a README file and generate a requirements.txt file")

import asyncio
import sys
from typing import Dict, Any, List
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langgraph.prebuilt import ToolNode
# pyrefly: ignore [missing-import]
from src.core.state import AgentState
# pyrefly: ignore [missing-import]
from src.core.orchestration.spawn_manager import AgentProcess
# pyrefly: ignore [missing-import]
from src.core.mcp.mcp_client import MCPClientManager


class OrchestrationCoordinator:
    """
    Main coordinator for Phase 125 Sub-Agent Engine.
    Integrates MCP Protocol via LangGraph ToolNode and ReAct loops.
    """

    def __init__(self, thread_id: str = "orchestrator-001"):
        self.thread_id = thread_id
        self.mcp_manager = MCPClientManager()
        self.graph = None # Will be built async or on first run

    async def _ensure_graph(self):
        """Ensures MCP is started and graph is built with active tools."""
        if self.graph:
            return
        
        # 1. Start MCP Client Manager (Parallel Startup)
        await self.mcp_manager.startup()
        
        # 2. Build Graph with Tools
        builder = StateGraph(AgentState)

        # Nodes
        builder.add_node("supervisor", self.supervisor_node)
        builder.add_node("execute_tasks", self.execute_tasks_node)
        builder.add_node("aggregator", self.aggregator_node)
        
        # Wave 2: MCP Tool Support
        tools = self.mcp_manager.get_tools_for_agent()
        if tools:
            builder.add_node("mcp_tools", ToolNode(tools))
            # Edges with ReAct Router
            builder.add_edge("execute_tasks", "mcp_tools")
            builder.add_conditional_edges(
                "mcp_tools",
                self.should_continue_reasoning,
                {
                    "continue": "supervisor", # Back to supervisor for re-planning
                    "end": "aggregator"
                }
            )
        else:
            builder.add_edge("execute_tasks", "aggregator")

        # Basic Flow
        builder.add_edge(START, "supervisor")
        builder.add_edge("supervisor", "execute_tasks")
        builder.add_edge("aggregator", END)

        self.graph = builder.compile()

    def should_continue_reasoning(self, state: AgentState) -> str:
        """
        Determines if tool results require further supervisor reasoning.
        (ReAct / Loop protection)
        """
        last_message = state["messages"][-1]
        # In a real scenario, we'd check if the tool output is an error or 
        # if the last message contains complex instructions.
        # Here we check if we've looped too many times.
        if len(state.get("mcp_tools_used", [])) > 5:
            return "end"
        
        # pyrefly: ignore [missing-attribute]
        if isinstance(last_message, ToolMessage) and "error" in last_message.content.lower():
             return "continue"
             
        return "end"

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
            "messages": [
                AIMessage(content=f"Supervisor split task into {len(tasks)} sub-tasks.")
            ],
            "pending_approval": False,  # Future IRD check
            "last_action": {"tasks": tasks},  # Use dict for passing tasks to next node
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
            p.spawn(
                [
                    sys_executable(),
                    "-c",
                    f"import time; print('Starting {task}'); time.sleep(5); print('Done {task}')",
                ]
            )
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
            "review_reports": [
                {"agent_id": p.agent_id, "task": p.task_name} for p in processes
            ],
        }

    async def aggregator_node(self, state: AgentState) -> Dict[str, Any]:
        """Finalizes the orchestration run."""
        return {
            "messages": [
                AIMessage(content="Final aggregation complete. All sub-agents synced.")
            ],
            "success_rate": 1.0,
        }

    async def run_async(self, task_prompt: str) -> Dict[str, Any]:
        """Async entry point for orchestration."""
        await self._ensure_graph()
        
        initial_state: AgentState = {
            "messages": [],
            "task_input": task_prompt,
            "failure_count": 0,
            "last_errors": [],
            "current_version": "v1.9.1",
            "risk_level": 1,
            "mcp_tools_used": [],
            "tool_outputs": [],
            "tool_errors": [],
            "last_action": {},
            "pending_approval": False,
            "approval_result": None,
            "thread_id": self.thread_id,
            "review_reports": [],
            "success_rate": 0.0
        }

        # Run the graph
        config = {"configurable": {"thread_id": self.thread_id}}
        # pyrefly: ignore [missing-attribute]
        final_state = await self.graph.ainvoke(initial_state, config=config)
        return final_state

    def run(self, task_prompt: str):
        """Entry point for orchestration."""
        return asyncio.run(self.run_async(task_prompt))


def sys_executable():
    import sys

    return sys.executable


if __name__ == "__main__":
    orchestrator = OrchestrationCoordinator()
    print("Running parallel orchestration test...")
    orchestrator.run("Create a README file and generate a requirements.txt file")

import logging
from typing import List, Dict, Any
from graphlib import TopologicalSorter, CycleError

from scripts.execution.schemas import ExecutionNode

logger = logging.getLogger(__name__)

def build_dag(consensus_result: Dict[str, Any]) -> List[ExecutionNode]:
    """
    Parses a ConsensusResult dictionary and builds a topologically sorted list
    of ExecutionNodes. If a cycle is detected, it falls back to a sequential
    flat list based on input order.
    """
    tasks_data = consensus_result.get("tasks", [])
    nodes = []
    
    # 1. Parse raw dicts into ExecutionNode objects
    for task in tasks_data:
        nodes.append(ExecutionNode(
            id=task.get("id", ""),
            role=task.get("role", "developer"),
            files=task.get("target_files", []),
            depends_on=task.get("dependencies", []),
            adopted_decision=task.get("adopted_decision")
        ))
        
    if not nodes:
        return []

    # 2. Build graph for topological sort
    graph = {n.id: n.depends_on for n in nodes}
    node_map = {n.id: n for n in nodes}
    
    ts = TopologicalSorter(graph)
    
    try:
        # Prepare graph and get sorted order
        # static_order() returns a generator of node IDs
        sorted_ids = list(ts.static_order())
        
        # In case some dependencies point to nodes that don't exist in task list,
        # we filter them out to avoid KeyError.
        sorted_nodes = [node_map[node_id] for node_id in sorted_ids if node_id in node_map]
        return sorted_nodes
        
    except CycleError as e:
        logger.warning(f"Cycle dependency detected in ConsensusResult: {e}. Falling back to sequential order.")
        # Fallback to the original order (sequential)
        return nodes

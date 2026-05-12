import os
import sys
import subprocess
from pathlib import Path

# Add scripts to path to find orchestrator if needed
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "scripts"))
from aa_constants import get_planning_dir

def graphify_query(question: str) -> str:
    """
    AutoAgent-TW Knowledge Graph Query Tool.
    Allows agents to query the project architecture using natural language.
    
    Args:
        question (str): The architectural or structural question.
        
    Returns:
        str: The response from the knowledge graph.
    """
    out_dir = get_planning_dir() / "graphify-out"
    
    cmd = ["graphify", "query", question, "--out", str(out_dir)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error querying graph: {e.stderr}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

def graphify_status() -> str:
    """Check the freshness and status of the knowledge graph."""
    from graphify_orchestrator import GraphifyOrchestrator
    orch = GraphifyOrchestrator()
    status = orch.get_status()
    return f"Status: {status.get('status', 'Unknown')}, Last Run: {status.get('last_run', 'N/A')}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(graphify_query(sys.argv[1]))

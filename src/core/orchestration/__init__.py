"""
AI Harness Orchestration Package
"""
from .coordinator import OrchestrationCoordinator
from .spawn_manager import AgentProcess

__version__ = "1.0.0"
__all__ = [
    "OrchestrationCoordinator",
    "AgentProcess",
]

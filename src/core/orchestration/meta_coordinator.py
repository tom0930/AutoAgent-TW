import logging
import threading
from typing import Dict, List, Optional, Any
from .agent_identity import CapabilityCard, AgentRole
from ...harness.streaming import event_bus, WorkflowEvent, EventType

logger = logging.getLogger("Orchestration.Meta")

class MetaCoordinator:
    """
    Top-level Orchestration Hub (Phase 171 v2.1).
    Manages global resources, global agent limits, and cross-squad coordination.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MetaCoordinator, cls).__new__(cls)
            return cls._instance

    def __init__(self, max_concurrent_agents: int = 4):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self.max_concurrent_agents = max_concurrent_agents
        self.active_agents: Dict[str, CapabilityCard] = {}
        self.active_squads: Dict[str, Any] = {} # SquadID: SquadCoordinator
        self._lock = threading.Lock()
        self._initialized = True
        logger.info(f"MetaCoordinator initialized. Max Concurrent Agents: {max_concurrent_agents}")

    def request_agent_spawn(self, card: CapabilityCard) -> bool:
        """
        Global resource gatekeeper.
        Checks if spawning a new agent is within global limits.
        """
        with self._lock:
            if len(self.active_agents) >= self.max_concurrent_agents:
                logger.warning(f"MetaCoordinator: Spawn rejected. Global limit ({self.max_concurrent_agents}) reached.")
                return False
            
            self.active_agents[card.agent_id] = card
            event_bus.emit(WorkflowEvent(
                EventType.AGENT_SPAWNED, 
                card.agent_id, 
                data={"role": card.role, "global_load": self.get_global_load()}
            ))
            return True

    def release_agent(self, agent_id: str):
        """Releases agent slot back to the pool."""
        with self._lock:
            if agent_id in self.active_agents:
                card = self.active_agents.pop(agent_id)
                event_bus.emit(WorkflowEvent(
                    EventType.AGENT_COMPLETED, 
                    agent_id, 
                    data={"role": card.role, "global_load": self.get_global_load()}
                ))

    def get_global_load(self) -> float:
        """Returns normalized load 0.0 to 1.0."""
        return len(self.active_agents) / self.max_concurrent_agents

# Singleton Instance
meta_coordinator = MetaCoordinator()

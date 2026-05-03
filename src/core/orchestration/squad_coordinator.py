import logging
import threading
import uuid
import time
from typing import List, Dict, Any, Callable
from .agent_identity import CapabilityCard, AgentRole
from .meta_coordinator import meta_coordinator
from .circuit_breaker import CircuitBreaker
from ...harness.streaming import event_bus, WorkflowEvent, EventType

logger = logging.getLogger("Orchestration.Squad")

class AgentWorker(threading.Thread):
    """Individual worker thread for an agent."""
    def __init__(self, card: CapabilityCard, task_fn: Callable, task_data: Dict[str, Any]):
        super().__init__(daemon=True, name=f"Agent-{card.agent_id}")
        self.card = card
        self.task_fn = task_fn
        self.task_data = task_data
        self.result = None
        self.error = None
        self.circuit_breaker = CircuitBreaker()

    def run(self):
        try:
            if not meta_coordinator.request_agent_spawn(self.card):
                self.error = "MetaCoordinator rejected spawn (limit reached)."
                return

            if not self.circuit_breaker.can_execute():
                self.error = "Circuit Breaker is OPEN."
                return

            # Execute task logic
            self.result = self.task_fn(self.task_data)
            self.circuit_breaker.record_success()
            
        except Exception as e:
            self.error = str(e)
            self.circuit_breaker.record_failure()
            event_bus.emit(WorkflowEvent(EventType.AGENT_FAILED, self.card.agent_id, data={"error": str(e)}))
        finally:
            meta_coordinator.release_agent(self.card.agent_id)

class SquadCoordinator:
    """
    Mid-level orchestrator for Agent Squads (Phase 171 v2.1).
    Manages a group of agents collaborating on a task set.
    """
    def __init__(self, name: str):
        self.squad_id = str(uuid.uuid4())[:8]
        self.name = name
        self.workers: List[AgentWorker] = []
        logger.info(f"Squad '{self.name}' ({self.squad_id}) initialized.")

    def add_agent_task(self, card: CapabilityCard, task_fn: Callable, task_data: Dict[str, Any]):
        """Adds a task to be executed by a specific agent role."""
        worker = AgentWorker(card, task_fn, task_data)
        self.workers.append(worker)

    def execute_all(self, wait: bool = True) -> List[Dict[str, Any]]:
        """Starts all agents in parallel."""
        event_bus.emit(WorkflowEvent(EventType.SQUAD_PROPOSED, self.squad_id, data={"name": self.name}))
        
        for worker in self.workers:
            worker.start()

        if not wait:
            return []

        results = []
        for worker in self.workers:
            worker.join(timeout=worker.card.ttl_seconds)
            results.append({
                "agent_id": worker.card.agent_id,
                "role": worker.card.role,
                "result": worker.result,
                "error": worker.error
            })
        
        event_bus.emit(WorkflowEvent(EventType.SQUAD_COMPLETED, self.squad_id, data={"name": self.name}))
        return results

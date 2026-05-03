import time
import queue
import threading
import logging
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol
from dataclasses import dataclass, field

logger = logging.getLogger("Harness.Streaming")

class EventType(Enum):
    TOOL_START = "tool_start"
    TOOL_END = "tool_end"
    MODEL_THINKING = "model_thinking"
    CHECKPOINT_SAVED = "checkpoint_saved"
    CONTEXT_COMPRESSED = "context_compressed"
    WORKFLOW_PAUSED = "workflow_paused"
    WORKFLOW_RESUMED = "workflow_resumed"
    ERROR = "error"
    
    # Phase 171 (New)
    AGENT_SPAWNED = "agent_spawned"
    AGENT_COMPLETED = "agent_completed"
    AGENT_FAILED = "agent_failed"
    SQUAD_PROPOSED = "squad_proposed"
    SQUAD_COMPLETED = "squad_completed"
    SUGGESTION_READY = "suggestion_ready"
    CRISIS_DETECTED = "crisis_detected"
    INTERVENTION_TRIGGERED = "intervention_triggered"

@dataclass
class WorkflowEvent:
    event_type: EventType
    workflow_id: str
    timestamp: float = field(default_factory=time.time)
    data: Dict[str, Any] = field(default_factory=dict)

class EventPublisher(Protocol):
    """Abstract interface for publishing events."""
    def publish(self, event: WorkflowEvent):
        ...

class StreamingEventBus:
    """
    In-memory priority event bus for workflow observability.
    Decouples event production from rendering/transmission.
    Supports Priority: CRISIS (0) > ERROR (1) > INFO (2) > LOG (3).
    """
    def __init__(self):
        self._subscribers: List[EventPublisher] = []
        self._event_queue = queue.PriorityQueue(maxsize=2000)
        self._stop_event = threading.Event()
        self._worker_thread = threading.Thread(target=self._process_queue, daemon=True, name="EventBus-Worker")
        self._worker_thread.start()

    def subscribe(self, publisher: EventPublisher):
        self._subscribers.append(publisher)

    def emit(self, event: WorkflowEvent):
        # Determine priority (Lower number = Higher priority)
        priority = 2 # Default Info
        if event.event_type.value in ["error", "crisis_detected"]:
            priority = 0
        elif event.event_type.value in ["intervention_triggered", "workflow_paused"]:
            priority = 1
        
        try:
            self._event_queue.put_nowait((priority, event.timestamp, event))
        except queue.Full:
            # Drop lowest priority event if queue is full
            try:
                self._event_queue.get_nowait()
                self._event_queue.put_nowait((priority, event.timestamp, event))
            except queue.Empty:
                pass

    def _process_queue(self):
        while not self._stop_event.is_set():
            try:
                # PriorityQueue returns (priority, timestamp, event)
                prio, ts, event = self._event_queue.get(timeout=0.1)
                for sub in self._subscribers:
                    try:
                        sub.publish(event)
                    except Exception as e:
                        logger.error(f"Subscriber failure: {e}")
                self._event_queue.task_done()
            except queue.Empty:
                continue

    def stop(self):
        self._stop_event.set()
        self._worker_thread.join(timeout=1.0)

class CLIEventPublisher:
    """Default implementation for CLI rendering using Rich."""
    def __init__(self, renderer: Optional[Any] = None):
        self.renderer = renderer

    def publish(self, event: WorkflowEvent):
        if self.renderer:
            self.renderer.render(event)
        else:
            # Fallback simple print if renderer not provided
            print(f"[{event.event_type.value.upper()}] {event.workflow_id}: {event.data}")

# Global bus instance for the process
event_bus = StreamingEventBus()

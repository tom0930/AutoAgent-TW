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
    In-memory event bus for workflow observability.
    Decouples event production from rendering/transmission.
    """
    def __init__(self):
        self._subscribers: List[EventPublisher] = []
        self._event_queue = queue.Queue(maxsize=1000)
        self._stop_event = threading.Event()
        self._worker_thread = threading.Thread(target=self._process_queue, daemon=True, name="EventBus-Worker")
        self._worker_thread.start()

    def subscribe(self, publisher: EventPublisher):
        self._subscribers.append(publisher)

    def emit(self, event: WorkflowEvent):
        try:
            self._event_queue.put_nowait(event)
        except queue.Full:
            # Drop oldest event if queue is full (Industrial standard for high-volume logs)
            try:
                self._event_queue.get_nowait()
                self._event_queue.put_nowait(event)
            except queue.Empty:
                pass

    def _process_queue(self):
        while not self._stop_event.is_set():
            try:
                event = self._event_queue.get(timeout=0.1)
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

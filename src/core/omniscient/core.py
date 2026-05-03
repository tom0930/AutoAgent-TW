import time
import logging
from enum import Enum
from typing import List, Dict, Any, Optional
from src.core.orchestration.agent_identity import CapabilityCard, AgentRole, TrustLevel
from src.harness.streaming import event_bus, WorkflowEvent, EventType

logger = logging.getLogger("Omniscient.Core")

class InterventionLevel(Enum):
    PASSIVE = "passive"           # 靜默觀察
    PROACTIVE_GENTLE = "gentle"   # 側邊欄建議
    ACTIVE = "active"             # 強制介入 (全螢幕診斷)

class OmniscientAgentCore:
    """
    Omniscient Assistant Brain (Phase 171 v2.1).
    Processes IDE/Agent events and manages the 3-tier intervention state machine.
    """
    def __init__(self, capability: Optional[CapabilityCard] = None):
        self.capability = capability or CapabilityCard(
            agent_id="omniscient-001",
            role=AgentRole.OMNISCIENT,
            trust_level=TrustLevel.LOW,
            allowed_tools=["workspace/status", "mempalace_search"]
        )
        self.current_level = InterventionLevel.PASSIVE
        self.history = []
        self.last_idle_time = time.time()
        
        # Thresholds (Configurable)
        self.idle_threshold = 8.0 # 8s idle for Proactive Gentle
        self.error_count_threshold = 3

    def on_event(self, event: WorkflowEvent):
        """Main event entry point from EventBus."""
        self.history.append(event)
        
        # 1. Update Idle Timer
        if event.event_type == EventType.TOOL_START:
            self.last_idle_time = time.time()

        # 2. State Transition Logic
        new_level = self._evaluate_intervention_level(event)
        if new_level != self.current_level:
            self._transition_to(new_level, event)

    def _evaluate_intervention_level(self, event: WorkflowEvent) -> InterventionLevel:
        """Determines required intervention based on event severity."""
        
        # ACTIVE: Crisis or Critical Errors
        if event.event_type in [EventType.CRISIS_DETECTED, EventType.AGENT_FAILED]:
            return InterventionLevel.ACTIVE
            
        # PROACTIVE GENTLE: Idle + Warnings or multi-lint
        elapsed_idle = time.time() - self.last_idle_time
        if elapsed_idle > self.idle_threshold:
             # Logic for PROACTIVE GENTLE could be triggered here 
             # (e.g. if event.data has lint_errors > 0)
             if event.event_type == EventType.SUGGESTION_READY:
                 return InterventionLevel.PROACTIVE_GENTLE
        
        return InterventionLevel.PASSIVE

    def _transition_to(self, level: InterventionLevel, trigger_event: WorkflowEvent):
        """Handles transition effects and emits notification."""
        old_level = self.current_level
        self.current_level = level
        
        logger.info(f"Omniscient: State Transition {old_level.value} -> {level.value}")
        
        event_bus.emit(WorkflowEvent(
            EventType.INTERVENTION_TRIGGERED,
            self.capability.agent_id,
            data={
                "old_level": old_level.value,
                "new_level": level.value,
                "reason": f"Triggered by {trigger_event.event_type.value}"
            }
        ))

    def generate_suggestion(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a proactive suggestion with evidence linking.
        (Integrates with EvidenceMemory in next step)
        """
        # Mock logic for Wave 3.1
        suggestion = {
            "title": "💡 建議優化代碼結構",
            "content": "偵測到多處重複邏輯，建議考慮重構為共用函數。",
            "severity": "medium",
            "evidence_link": "mempalace://room/core-refactor",
            "timestamp": time.time()
        }
        event_bus.emit(WorkflowEvent(EventType.SUGGESTION_READY, self.capability.agent_id, data=suggestion))
        return suggestion

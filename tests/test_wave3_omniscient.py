import unittest
import time
import os
import shutil
from src.core.omniscient.core import OmniscientAgentCore, InterventionLevel
from src.core.omniscient.feedback_manager import FeedbackManager
from src.core.omniscient.suggestion_engine import SuggestionEngine
from src.harness.streaming import WorkflowEvent, EventType

class TestWave3Omniscient(unittest.TestCase):
    def setUp(self):
        self.test_dir = ".agent-state/test_omniscient"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        self.feedback = FeedbackManager(storage_path=os.path.join(self.test_dir, "feedback.json"))
        self.core = OmniscientAgentCore()
        self.engine = SuggestionEngine(self.core, self.feedback)

    def test_state_machine_passive_to_active(self):
        # Start at PASSIVE
        self.assertEqual(self.core.current_level, InterventionLevel.PASSIVE)
        
        # Trigger CRISIS -> Should jump to ACTIVE
        self.core.on_event(WorkflowEvent(EventType.CRISIS_DETECTED, "wf-1"))
        self.assertEqual(self.core.current_level, InterventionLevel.ACTIVE)

    def test_idle_proactive_gentle(self):
        self.core.idle_threshold = 0.5 # Reduce for test
        self.core.on_event(WorkflowEvent(EventType.TOOL_START, "wf-1"))
        
        # Wait for idle
        time.sleep(0.7)
        
        # Emit a suggestion -> Should move to GENTLE
        self.core.on_event(WorkflowEvent(EventType.SUGGESTION_READY, "wf-1"))
        self.assertEqual(self.core.current_level, InterventionLevel.PROACTIVE_GENTLE)

    def test_feedback_learning(self):
        # Record some negative feedback
        self.feedback.record_feedback("sug-1", False)
        self.feedback.record_feedback("sug-2", False)
        
        metrics = self.feedback.get_performance_metrics()
        self.assertEqual(metrics["satisfaction_score"], 0.0)
        
        # SuggestionEngine should adjust sensitivity
        adj = self.engine.get_sensitivity_adjustment()
        self.assertEqual(adj, 0.5)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

if __name__ == "__main__":
    unittest.main()

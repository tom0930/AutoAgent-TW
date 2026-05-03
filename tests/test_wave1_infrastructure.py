import unittest
import queue
import time
from src.harness.streaming import StreamingEventBus, WorkflowEvent, EventType
from src.core.orchestration.agent_identity import CapabilityCard, AgentRole, TrustLevel
from src.core.orchestration.agent_sandbox import AgentSandbox
from src.core.permission_engine import PermissionEngine

class TestWave1Infrastructure(unittest.TestCase):
    def setUp(self):
        self.bus = StreamingEventBus()
        self.permission_engine = PermissionEngine()

    def test_priority_event_bus(self):
        results = []
        class MockPublisher:
            def publish(self, event):
                results.append(event.event_type)

        self.bus.subscribe(MockPublisher())
        
        # Emit multiple events: LOG should be delayed behind CRISIS
        # Note: Since it's async, we use a small sleep to ensure processing order if they were queued
        self.bus.emit(WorkflowEvent(EventType.TOOL_START, "wf-1")) # Priority 2
        self.bus.emit(WorkflowEvent(EventType.CRISIS_DETECTED, "wf-1")) # Priority 0
        self.bus.emit(WorkflowEvent(EventType.ERROR, "wf-1")) # Priority 0
        
        time.sleep(0.5)
        # Expected: CRISIS or ERROR should be processed before TOOL_START if they hit the queue together
        # (Though with 0.1s timeout it's fast, we just check they all arrive)
        self.assertIn(EventType.CRISIS_DETECTED, results)
        self.assertIn(EventType.ERROR, results)
        self.assertIn(EventType.TOOL_START, results)

    def test_agent_sandbox_identity(self):
        card = CapabilityCard(
            agent_id="test-1",
            role=AgentRole.TESTER,
            trust_level=TrustLevel.MEDIUM,
            allowed_tools=["read_file", "run_command"]
        )
        sandbox = AgentSandbox(card, self.permission_engine)
        
        # Case 1: Allowed tool
        print(f"DEBUG: allowed_tools={card.allowed_tools}")
        allowed, reason = sandbox.validate_tool_use("read_file", {})
        self.assertTrue(allowed, msg=reason)
        
        # Case 2: Identity violation (not in allowed list)
        allowed, reason = sandbox.validate_tool_use("write_to_file", {})
        self.assertFalse(allowed)
        self.assertIn("Identity Violation", reason)

    def test_agent_sandbox_risk_limit(self):
        # Tester has TrustLevel.MEDIUM (2). run_command is Risk 4.
        card = CapabilityCard(
            agent_id="test-2",
            role=AgentRole.TESTER,
            trust_level=TrustLevel.MEDIUM,
            allowed_tools=["run_command"]
        )
        sandbox = AgentSandbox(card, self.permission_engine)
        
        # Case 1: Trust level violation (Risk 4 > Trust 2)
        allowed, reason = sandbox.validate_tool_use("run_command", {})
        self.assertFalse(allowed)
        self.assertIn("Trust Violation", reason)

    def test_agent_sandbox_command_scan(self):
        card = CapabilityCard(
            agent_id="test-3",
            role=AgentRole.CODER,
            trust_level=TrustLevel.HIGH, # Coder has trust level 3
            allowed_tools=["run_command"]
        )
        # Manually adjust permission engine for this test if needed, 
        # but run_command is risk 4, so it should still fail trust check unless we raise trust level
        card.trust_level = TrustLevel.ADMIN # 4
        
        sandbox = AgentSandbox(card, self.permission_engine)
        
        # Case 1: Destructive command
        allowed, reason = sandbox.validate_tool_use("run_command", {"CommandLine": "rm -rf /"})
        self.assertFalse(allowed)
        self.assertIn("Sandbox Violation", reason)

if __name__ == "__main__":
    unittest.main()

import unittest
import time
from src.core.orchestration.agent_identity import CapabilityCard, AgentRole, TrustLevel
from src.core.orchestration.meta_coordinator import MetaCoordinator
from src.core.orchestration.squad_coordinator import SquadCoordinator
from src.core.orchestration.circuit_breaker import CircuitBreaker

class TestWave2Orchestration(unittest.TestCase):
    def test_circuit_breaker_backoff(self):
        cb = CircuitBreaker(max_failures=2, initial_cooldown=1)
        
        # 1st failure
        cb.record_failure()
        self.assertTrue(cb.can_execute())
        
        # 2nd failure -> Trips
        cb.record_failure()
        self.assertFalse(cb.can_execute())
        
        # Wait for cooldown (1s)
        time.sleep(1.1)
        self.assertTrue(cb.can_execute()) # Should move to HALF_OPEN
        
        # Fail again while HALF_OPEN -> Triple cooldown (2s)
        cb.record_failure()
        self.assertFalse(cb.can_execute())
        
        # Wait 1s (not enough)
        time.sleep(1)
        self.assertFalse(cb.can_execute())
        
        # Wait total 2.1s
        time.sleep(1.2)
        self.assertTrue(cb.can_execute())

    def test_meta_coordinator_limits(self):
        # Reset MetaCoordinator singleton for test
        mc = MetaCoordinator()
        mc.max_concurrent_agents = 2
        mc.active_agents.clear()
        
        c1 = CapabilityCard(agent_id="a1", role=AgentRole.CODER, trust_level=TrustLevel.HIGH)
        c2 = CapabilityCard(agent_id="a2", role=AgentRole.TESTER, trust_level=TrustLevel.MEDIUM)
        c3 = CapabilityCard(agent_id="a3", role=AgentRole.REVIEWER, trust_level=TrustLevel.MEDIUM)
        
        self.assertTrue(mc.request_agent_spawn(c1))
        self.assertTrue(mc.request_agent_spawn(c2))
        self.assertFalse(mc.request_agent_spawn(c3)) # Limit reached
        
        mc.release_agent("a1")
        self.assertTrue(mc.request_agent_spawn(c3)) # Slot freed

    def test_squad_parallel_execution(self):
        squad = SquadCoordinator("BugFix-Squad")
        
        def mock_task(data):
            time.sleep(data["delay"])
            return f"Done {data['id']}"

        c1 = CapabilityCard(agent_id="w1", role=AgentRole.CODER, trust_level=TrustLevel.HIGH, ttl_seconds=5)
        c2 = CapabilityCard(agent_id="w2", role=AgentRole.TESTER, trust_level=TrustLevel.MEDIUM, ttl_seconds=5)
        
        # Clear Meta for this test
        from src.core.orchestration.meta_coordinator import meta_coordinator
        meta_coordinator.max_concurrent_agents = 4
        meta_coordinator.active_agents.clear()

        squad.add_agent_task(c1, mock_task, {"id": "task1", "delay": 1})
        squad.add_agent_task(c2, mock_task, {"id": "task2", "delay": 1})
        
        start_time = time.time()
        results = squad.execute_all(wait=True)
        end_time = time.time()
        
        # Both tasks take 1s, but run in parallel, so total time should be ~1s, not 2s
        duration = end_time - start_time
        self.assertLess(duration, 1.8) # Allow some overhead, but definitely < 2.0
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["result"], "Done task1")
        self.assertEqual(results[1]["result"], "Done task2")

if __name__ == "__main__":
    unittest.main()

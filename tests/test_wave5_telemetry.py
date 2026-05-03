import unittest
from src.core.omniscient.telemetry import telemetry
from src.core.omniscient.suggestion_engine import SuggestionEngine
from src.core.omniscient.core import OmniscientAgentCore
from src.core.omniscient.feedback_manager import FeedbackManager

class TestWave5Telemetry(unittest.TestCase):
    def test_telemetry_aggregation(self):
        # Record some dummy data
        telemetry.record_squad_result("sq-1", True)
        telemetry.record_squad_result("sq-2", False)
        telemetry.record_token_usage("coder", 500)
        telemetry.record_token_usage("reviewer", 200)
        
        summary = telemetry.get_summary()
        self.assertEqual(summary["success_rate"], 50.0)
        self.assertEqual(summary["total_tokens"], 700)
        self.assertIn("coder", summary["token_by_role"])

    def test_l0_scan_security(self):
        core = OmniscientAgentCore()
        feedback = FeedbackManager(storage_path=".agent-state/test_l0_feedback.json")
        engine = SuggestionEngine(core, feedback)
        
        bad_code = "api_key = 'AKIA_MOCKED_SECRET_KEY'\npassword = '123456'\n"
        sugs = engine.run_l0_scan("test.py", bad_code)
        
        # Should detect 2 security issues
        security_sugs = [s for s in sugs if s["type"] == "security"]
        self.assertEqual(len(security_sugs), 2)
        self.assertEqual(security_sugs[0]["severity"], "high")

    def test_l0_scan_complexity(self):
        core = OmniscientAgentCore()
        feedback = FeedbackManager(storage_path=".agent-state/test_l0_feedback.json")
        engine = SuggestionEngine(core, feedback)
        
        long_code = "\n" * 600
        sugs = engine.run_l0_scan("large_file.py", long_code)
        
        self.assertTrue(any(s["type"] == "refactor" for s in sugs))

if __name__ == "__main__":
    unittest.main()

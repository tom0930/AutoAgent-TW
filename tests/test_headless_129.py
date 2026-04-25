import unittest
import os
import sys
import io
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.security.log_sanitizer import LogSanitizer
from src.harness.cli.main import HarnessCLI

class TestPhase129Headless(unittest.TestCase):

    def test_log_sanitizer_redaction(self):
        """Verify that sensitive tokens are redacted."""
        sanitizer = LogSanitizer()
        
        # Test tokens
        gemini_key = "AIzaSyAz1234567890abcdefGHIJKLMnopqrst"
        anthropic_key = "sk-ant-api03-abcdefghijklmn-1234567890-ABCDEFGHIJKLMN"
        github_pat = "ghp_abcdefghijklmnopqrstuvwxyz1234567890"
        
        test_string = f"Connecting with {gemini_key}, {anthropic_key} and {github_pat}"
        sanitized = sanitizer.sanitize(test_string)
        
        self.assertNotIn(gemini_key, sanitized)
        self.assertNotIn(anthropic_key, sanitized)
        self.assertNotIn(github_pat, sanitized)
        self.assertEqual(sanitized.count("[REDACTED]"), 3)

    def test_headless_env_activation(self):
        """Verify that --headless flag sets environment variable."""
        cli = HarnessCLI(["--headless", "doctor"])
        
        # We need to mock run or just check how it sets env in run()
        with patch("src.harness.cli.main.HarnessCLI._dispatch", return_value=0):
            with patch("sys.stdout", new=io.StringIO()):
                cli.run()
                self.assertEqual(os.environ.get("AA_HEADLESS"), "1")

    def test_orchestration_loop_limit_headless(self):
        """Verify loop limit enforcement in headless mode."""
        # This requires mocking the coordinator and state
        from src.core.orchestration.coordinator import OrchestrationCoordinator
        
        os.environ["AA_HEADLESS"] = "1"
        os.environ["AA_MAX_LOOPS"] = "2"
        
        coord = OrchestrationCoordinator()
        mock_state = {"messages": [MagicMock(content="no error")], "mcp_tools_used": ["tool1", "tool2"]}
        
        # Should return 'end' because tool_used >= max_loops
        result = coord.should_continue_reasoning(mock_state)
        self.assertEqual(result, "end")

if __name__ == "__main__":
    unittest.main()

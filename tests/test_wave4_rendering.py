import unittest
from src.core.renderers.cli import CliLiveRenderer
from src.core.renderers.web import WebPanelRenderer

class TestWave4Rendering(unittest.TestCase):
    def test_cli_renderer_state_tracking(self):
        renderer = CliLiveRenderer()
        
        # Simulate agent update
        renderer.update_agent_status("a1", "Thinking", {"role": "Coder"})
        self.assertIn("a1", renderer.agents)
        self.assertEqual(renderer.agents["a1"]["role"], "Coder")
        
        # Simulate suggestion
        sug = {"title": "Test Sug", "content": "Hello"}
        renderer.display_suggestion(sug)
        self.assertEqual(len(renderer.suggestions), 1)

    def test_web_renderer_payload(self):
        sent_messages = []
        class MockClient:
            def send(self, msg):
                sent_messages.append(msg)
        
        renderer = WebPanelRenderer(websocket_client=MockClient())
        renderer.display_suggestion({"title": "Web Sug"})
        
        self.assertEqual(len(sent_messages), 1)
        self.assertIn("Web Sug", sent_messages[0])

if __name__ == "__main__":
    unittest.main()

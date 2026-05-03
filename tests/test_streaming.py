import time
import unittest
from io import StringIO
from unittest.mock import MagicMock, patch
from src.harness.streaming import event_bus, WorkflowEvent, EventType, CLIEventPublisher
from src.harness.cli.event_renderer import CLIEventRenderer

class TestStreaming(unittest.TestCase):
    def test_event_bus_delivery(self):
        """Verify that events emitted to the bus reach the publisher."""
        mock_publisher = MagicMock()
        event_bus.subscribe(mock_publisher)
        
        event = WorkflowEvent(
            event_type=EventType.CHECKPOINT_SAVED,
            workflow_id="test_wf",
            data={"step_id": "42"}
        )
        
        event_bus.emit(event)
        
        # Wait for async delivery
        time.sleep(0.5)
        
        mock_publisher.publish.assert_called_with(event)

    def test_cli_renderer_output(self):
        """Verify CLI Renderer produces Rich-formatted output (smoke test)."""
        renderer = CLIEventRenderer()
        # Mock console.print to capture output or just verify it's called
        with patch.object(renderer.console, 'print') as mock_print:
            event = WorkflowEvent(
                event_type=EventType.TOOL_START,
                workflow_id="test_wf",
                data={"tool": "ls"}
            )
            renderer.render(event)
            mock_print.assert_called()
            # Check if ASCII symbol '>' is in the call
            args, _ = mock_print.call_args
            self.assertIn(">", args[0])

if __name__ == '__main__':
    unittest.main()

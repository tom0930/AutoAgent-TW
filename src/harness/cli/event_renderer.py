import logging
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from ..streaming import WorkflowEvent, EventType

logger = logging.getLogger("Harness.CLI.Renderer")

class CLIEventRenderer:
    """
    Renders Workflow Events to the CLI using Rich.
    Provides a dynamic 'dashboard-like' feel for long-running tasks.
    """
    def __init__(self):
        self.console = Console()
        self.active_tools = {} # tool_id -> start_time
        
        # Mapping Event types to symbols/colors (ASCII-safe fallbacks)
        self.symbols = {
            EventType.TOOL_START: ">",
            EventType.TOOL_END: "OK",
            EventType.MODEL_THINKING: "?",
            EventType.CHECKPOINT_SAVED: "S",
            EventType.CONTEXT_COMPRESSED: "C",
            EventType.WORKFLOW_PAUSED: "||",
            EventType.WORKFLOW_RESUMED: ">>",
            EventType.ERROR: "!!"
        }

    def render(self, event: WorkflowEvent):
        symbol = self.symbols.get(event.event_type, "•")
        
        try:
            if event.event_type == EventType.TOOL_START:
                tool_name = event.data.get("tool", "unknown")
                self.console.print(f"[bold cyan]{symbol} Tool Starting:[/bold cyan] {tool_name}")
                
            elif event.event_type == EventType.TOOL_END:
                tool_name = event.data.get("tool", "unknown")
                duration = event.data.get("duration", 0)
                self.console.print(f"[bold green]{symbol} Tool Finished:[/bold green] {tool_name} ({duration:.2f}s)")
                
            elif event.event_type == EventType.MODEL_THINKING:
                self.console.print(f"[italic magenta]{symbol} AI is thinking...[/italic magenta]")
                
            elif event.event_type == EventType.CHECKPOINT_SAVED:
                step = event.data.get("step_id", "?")
                self.console.print(f"[dim blue]{symbol} Checkpoint saved (# {step})[/dim blue]")
                
            elif event.event_type == EventType.CONTEXT_COMPRESSED:
                ratio = event.data.get("ratio", 0)
                self.console.print(f"[yellow]{symbol} Context Compressed (Reduction: {ratio:.1%})[/yellow]")
                
            elif event.event_type == EventType.WORKFLOW_PAUSED:
                self.console.print(f"[bold red]{symbol} Workflow PAUSED (Partial state saved)[/bold red]")
                
            elif event.event_type == EventType.ERROR:
                msg = event.data.get("message", "Unknown error")
                self.console.print(f"[bold red]{symbol} ERROR:[/bold red] {msg}", style="blink")
                
            else:
                self.console.print(f"{symbol} {event.event_type.value}: {event.data}")
        except UnicodeEncodeError:
            # Fallback to ASCII-only for old Windows consoles (CP950 etc.)
            self.console.print(f"[{event.event_type.value.upper()}] {event.workflow_id}: {event.data}")

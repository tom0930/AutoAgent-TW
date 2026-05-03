import logging
from typing import Dict, Any, List
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from .base import BaseRenderer

logger = logging.getLogger("Renderer.CLI")

class CliLiveRenderer(BaseRenderer):
    """
    Real-time Terminal Dashboard using 'rich' (Phase 171 v2.1).
    Provides side-by-side view of Agents, Suggestions, and Logs.
    """
    def __init__(self):
        self.console = Console()
        self.layout = self._setup_layout()
        self.live = Live(self.layout, refresh_per_second=4, screen=False)
        
        # State Storage
        self.agents = {} # id -> {role, status, load}
        self.suggestions = []
        self.logs = [] # Last 5 logs

    def _setup_layout(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        layout["main"].split_row(
            Layout(name="agent_panel", ratio=1),
            Layout(name="suggestion_panel", ratio=1)
        )
        return layout

    def start(self):
        self.live.start()

    def stop(self):
        self.live.stop()

    def update_agent_status(self, agent_id: str, status: str, data: Dict[str, Any] = None):
        data = data or {}
        self.agents[agent_id] = {
            "role": data.get("role", "Unknown"),
            "status": status,
            "load": data.get("global_load", 0.0)
        }
        self._refresh_ui()

    def display_suggestion(self, suggestion: Dict[str, Any]):
        self.suggestions.insert(0, suggestion)
        self.suggestions = self.suggestions[:3] # Keep last 3
        self._refresh_ui()

    def display_squad_metrics(self, squad_id: str, metrics: Dict[str, Any]):
        # Custom logic for squad view
        pass

    def notify_crisis(self, message: str, diagnostic_data: Dict[str, Any]):
        self.console.print(Panel(f"[bold red]CRISIS DETECTED[/bold red]\n{message}", border_style="red"))

    def _refresh_ui(self):
        # 1. Update Agent Table
        table = Table(title="🤖 Active Agents", expand=True)
        table.add_column("Agent ID", style="cyan")
        table.add_column("Role", style="magenta")
        table.add_column("Status", style="green")
        
        for aid, info in self.agents.items():
            table.add_row(aid, info["role"], info["status"])
        
        self.layout["agent_panel"].update(Panel(table, title="[bold]Squad Status[/bold]"))

        # 2. Update Suggestion Panel
        sug_content = ""
        for sug in self.suggestions:
            sug_content += f"• [yellow]{sug.get('title')}[/yellow]\n  {sug.get('content')}\n\n"
        
        self.layout["suggestion_panel"].update(Panel(sug_content, title="[bold]Proactive Suggestions[/bold]"))
        
        # 3. Header/Footer
        self.layout["header"].update(Panel("AutoAgent-TW [bold blue]Phase 171 Enhanced[/bold blue] Dashboard"))
        self.layout["footer"].update(Panel(f"System Load: {len(self.agents)} Agents Active"))

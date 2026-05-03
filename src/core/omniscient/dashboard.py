import logging
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from .telemetry import telemetry

logger = logging.getLogger("Omniscient.Dashboard")

class DashboardController:
    """
    Controller for the /aa-dashboard command (Phase 171 v2.1).
    Renders telemetry data to the console.
    """
    def __init__(self):
        self.console = Console()

    def render(self):
        summary = telemetry.get_summary()
        
        # 1. Main Stats Panel
        stats_table = Table(show_header=False, box=None)
        stats_table.add_row("Squad Success Rate", f"[bold green]{summary['success_rate']}%[/bold green]")
        stats_table.add_row("Total Tokens", f"[bold yellow]{summary['total_tokens']}[/bold yellow]")
        stats_table.add_row("Avg Intervention Latency", f"[bold cyan]{summary['avg_latency_ms']}ms[/bold cyan]")
        
        # 2. Token by Role Table
        token_table = Table(title="💰 Token Cost by Role")
        token_table.add_column("Role", style="magenta")
        token_table.add_column("Tokens", style="yellow")
        
        for role, tokens in summary["token_by_role"].items():
            token_table.add_row(role, str(tokens))
            
        # 3. Overall Display
        self.console.print("\n")
        self.console.print(Panel(
            Columns([stats_table, token_table]),
            title="[bold blue]AutoAgent-TW Omniscient Dashboard[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        ))
        self.console.print("\n")

# Singleton instance
dashboard = DashboardController()

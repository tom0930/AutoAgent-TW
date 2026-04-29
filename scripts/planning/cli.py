# scripts/planning/cli.py
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, Tree
from typing import List, Optional
import json
import os
from schemas import DecisionMatrix, ConsensusResult

class ParallelPlanningCLI:
    def __init__(self):
        self.console = Console()

    def display_plan_progress(self, agents: List[str]):
        """
        Visualizes the parallel execution of multiple planning agents using a Rich Tree.
        In an actual async run, this would be dynamically updated.
        """
        tree = Tree("[bold blue]🚀 Parallel Planning Engine[/bold blue]")
        
        for agent in agents:
            # Mock progress display
            tree.add(f"[green]✓[/green] {agent} Agent (Completed)")
            
        tree.add("[yellow]⚡[/yellow] Synthesizer: Resolving conflicts...")
        self.console.print(Panel(tree, title="Execution Progress", border_style="cyan"))

    def present_decision_matrix(self, matrix: DecisionMatrix) -> Optional[int]:
        """
        Legacy method for DecisionMatrix. Kept for backward compatibility.
        """
        # ... (Implementation preserved for compatibility if needed, though we primarily use ConsensusResult now)
        pass
        
    def present_consensus_result(self, result: ConsensusResult):
        """
        Presents the final consensus result and score.
        """
        status_color = "green" if result.status == "CONSENSUS" else "red" if result.status == "VETO" else "yellow"
        
        self.console.print(f"\n[bold {status_color}]⚖️  Consensus Status: {result.status}[/bold {status_color}]")
        self.console.print(f"[bold cyan]Consensus Score:[/bold cyan] {result.score:.2f}")
        self.console.print(f"[bold cyan]Adopted Decision:[/bold cyan] {result.adopted_decision}")
        
        if result.notes:
            self.console.print("\n[bold]Notes:[/bold]")
            for note in result.notes:
                self.console.print(f"  - {note}")
                
        self.console.print(f"\n[dim]Audit log saved to: {result.audit_path}[/dim]\n")

    def apply_resource_governance(self, requested_concurrency: int, current_token_budget_percent: float) -> int:
        """
        Dynamically scales down concurrency if token budget is low.
        """
        if current_token_budget_percent < 0.3:
            self.console.print("[yellow]⚠️ Low token budget (<30%). Scaling down concurrency to 2.[/yellow]")
            return min(requested_concurrency, 2)
        return requested_concurrency

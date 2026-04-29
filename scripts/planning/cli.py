# scripts/planning/cli.py
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, Tree
from typing import List, Optional
import json
import os
from schemas import DecisionMatrix

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
        Presents the decision matrix to the user and asks for a selection.
        """
        self.console.print("\n[bold red]⚠️  Architectural Conflict Detected[/bold red]")
        self.console.print(f"[white]{matrix.conflict_summary}[/white]\n")
        
        for idx, opt in enumerate(matrix.options, start=1):
            self.console.print(f"[bold cyan]Option {idx}: {opt.title}[/bold cyan] (Risk: {opt.risk_level})")
            self.console.print(f"  [green]Pros:[/green] {', '.join(opt.pros)}")
            self.console.print(f"  [red]Cons:[/red] {', '.join(opt.cons)}\n")
            
        try:
            choice = input("Enter your choice (1/2/... or 0 to abort): ")
            choice_int = int(choice)
            if choice_int > 0 and choice_int <= len(matrix.options):
                # Save user decision
                os.makedirs(".agent-state", exist_ok=True)
                with open(".agent-state/user_decision.json", "w") as f:
                    json.dump({"selected_option": choice_int}, f)
                return choice_int
            return None
        except ValueError:
            self.console.print("[red]Invalid selection.[/red]")
            return None

    def apply_resource_governance(self, requested_concurrency: int, current_token_budget_percent: float) -> int:
        """
        Dynamically scales down concurrency if token budget is low.
        """
        if current_token_budget_percent < 0.3:
            self.console.print("[yellow]⚠️ Low token budget (<30%). Scaling down concurrency to 2.[/yellow]")
            return min(requested_concurrency, 2)
        return requested_concurrency

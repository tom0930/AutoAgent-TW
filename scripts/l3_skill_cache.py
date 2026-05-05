import os
import json
import argparse
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

class L3SkillCache:
    def __init__(self, config_path: str, index_path: str):
        self.console = Console()
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            with open(index_path, 'r', encoding='utf-8') as f:
                self.index = json.load(f)
        except Exception as e:
            self.console.print(f"[bold red]Error loading configuration or index:[/bold red] {e}")
            sys.exit(1)
        
        self.entries = self.index.get('entries', [])

    def search(self, query: str, top_k: int = 5):
        query_terms = query.lower().split()
        results = []

        for entry in self.entries:
            # Skip blocked items
            if entry.get('risk', 0) >= self.config.get('security', {}).get('blocked_risk_level', 2):
                continue

            score = 0
            name = entry.get('name', '').lower()
            desc = entry.get('description', '').lower()
            tags = [t.lower() for t in entry.get('tags', [])]
            category = entry.get('category', '').lower()

            for term in query_terms:
                # Name matching
                if term == name: score += 2.0
                elif term in name: score += 1.5
                
                # Description matching
                if term in desc: score += 1.0
                
                # Tags matching
                if term in tags: score += 1.2
                
                # Category matching
                if term in category: score += 0.8

            if score >= self.config.get('search', {}).get('score_threshold', 0.6):
                results.append((score, entry))

        # Sort by score descending
        results.sort(key=lambda x: x[0], reverse=True)
        return results[:top_k]

    def read_skill(self, skill_path: str):
        try:
            path = Path(skill_path)
            if not path.exists():
                return None
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            self.console.print(f"[bold red]Error reading skill file:[/bold red] {e}")
            return None

    def list_sources(self):
        table = Table(title="L3 Cache Sources")
        table.add_column("Repo Name", style="cyan")
        table.add_column("URL", style="blue")
        table.add_column("Priority", style="magenta")
        table.add_column("Status", style="green")

        l3_root = Path(self.config.get('l3_cache_root', 'D:\\git'))
        for repo in self.config.get('repos', []):
            status = "Ready" if (l3_root / repo['name']).exists() else "Missing"
            table.add_row(
                repo['name'],
                repo['url'],
                str(repo['priority']),
                f"[{'green' if status == 'Ready' else 'red'}]{status}[/]"
            )
        self.console.print(table)

    def run_report(self):
        ledger_path = Path("z:/AutoAgent-TW/data/l3_skill_ledger.jsonl")
        if not ledger_path.exists():
            self.console.print("[yellow]No skill ledger found. Usage data is currently empty.[/yellow]")
            return

        stats = {}
        try:
            with open(ledger_path, 'r', encoding='utf-8') as f:
                for line in f:
                    entry = json.loads(line)
                    sid = entry.get('skill_id')
                    if not sid: continue
                    
                    if sid not in stats:
                        stats[sid] = {"uses": 0, "fixes": 0, "total_score": 0.0, "last_used": ""}
                    
                    if entry.get('event') == 'used':
                        stats[sid]["uses"] += 1
                        stats[sid]["total_score"] += entry.get('score', 0.0)
                        stats[sid]["last_used"] = entry.get('timestamp', '')[:10]
                    elif entry.get('event') == 'correlated_fix':
                        stats[sid]["fixes"] += 1
        except Exception as e:
            self.console.print(f"[bold red]Error parsing ledger:[/bold red] {e}")
            return

        table = Table(title="L3 Skill Quality Report")
        table.add_column("Skill ID", style="cyan")
        table.add_column("Uses", style="magenta", justify="right")
        table.add_column("Fixes", style="red", justify="right")
        table.add_column("Avg Score", style="blue", justify="right")
        table.add_column("Quality Score", style="bold green", justify="right")
        table.add_column("Action", style="white")

        import math
        for sid, data in stats.items():
            avg_score = data["total_score"] / max(data["uses"], 1)
            fix_rate = data["fixes"] / max(data["uses"], 1)
            
            # Quality formula: 0.4*success + 0.3*score + 0.2*usage - 0.5*fix_rate
            # Simplified for now:
            success_score = 1.0 - fix_rate
            usage_bonus = min(math.log(data["uses"] + 1) / 5.0, 0.2)
            quality = (0.4 * success_score) + (0.3 * (avg_score/2.5)) + usage_bonus
            
            action = "STABLE"
            if quality >= 0.8: action = "[bold green]PROBE L2[/]"
            elif quality < 0.4: action = "[bold red]BLACKLIST[/]"
            elif fix_rate > 0.5: action = "[yellow]WARN (BUGGY)[/]"

            table.add_row(
                sid,
                str(data["uses"]),
                str(data["fixes"]),
                f"{avg_score:.2f}",
                f"{quality:.2f}",
                action
            )

        self.console.print(table)
        self.console.print("\n[dim]Quality Score = 0.4*(1-fix_rate) + 0.3*(avg_score/2.5) + 0.2*(log usage)[/dim]")

    def display_search_results(self, results):
        if not results:
            self.console.print("[yellow]No matching L3 skills found.[/yellow]")
            return

        table = Table(title=f"L3 Cache Hits (Top {len(results)})")
        table.add_column("Score", style="bold green")
        table.add_column("Skill ID", style="cyan")
        table.add_column("Repo", style="magenta")
        table.add_column("Description", style="white")

        for score, entry in results:
            table.add_row(
                f"{score:.2f}",
                entry['id'],
                entry['repo'],
                entry['description'][:80] + "..." if len(entry['description']) > 80 else entry['description']
            )
        self.console.print(table)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="L3 Skill Cache Engine")
    parser.add_argument("--search", type=str, help="Search query")
    parser.add_argument("--read", type=str, help="Path to skill file to read")
    parser.add_argument("--sources", action="store_true", help="List available sources")
    parser.add_argument("--rebuild-index", action="store_true", help="Rebuild master index")
    parser.add_argument("--report", action="store_true", help="Generate quality report")
    args = parser.parse_args()

    config_path = "z:/AutoAgent-TW/config/l3_config.json"
    index_path = "z:/AutoAgent-TW/data/l3_master_index.json"
    
    cache = L3SkillCache(config_path, index_path)

    if args.search:
        results = cache.search(args.search)
        cache.display_search_results(results)
    elif args.read:
        content = cache.read_skill(args.read)
        if content:
            print(content)
        else:
            print(f"Error: Skill not found at {args.read}", file=sys.stderr)
    elif args.sources:
        cache.list_sources()
    elif args.rebuild_index:
        import subprocess
        subprocess.run([sys.executable, "scripts/build_l3_index.py"])
    elif args.report:
        cache.run_report()
    else:
        parser.print_help()

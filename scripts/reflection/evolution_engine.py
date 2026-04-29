#!/usr/bin/env python3
"""
AutoAgent-TW Evolution Engine (Phase 166: Wave 4)
=================================================
L3 Evolutionary Reflection Engine.
Runs monthly or after major milestones.
Analyzes the entire episodic memory buffer and verified patches
to generate a capability heatmap and meta-learning suggestions.
"""

import json
import os
import sys
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path(os.getcwd())
LOG_FILE = WORKSPACE / ".agent-state" / "reflection_log.jsonl"
REPORT_FILE = WORKSPACE / ".planning" / "EVOLUTION_REPORT.md"

def generate_heatmap(logs: list) -> dict:
    """Generates a capability heatmap based on historical failure density."""
    category_counts = defaultdict(int)
    for log in logs:
        for failure in log.get("failures", []):
            cat = failure.get("category", "unknown")
            category_counts[cat] += 1
            
    return dict(category_counts)

def generate_report(heatmap: dict):
    """Generates the EVOLUTION_REPORT.md."""
    lines = [
        "# AutoAgent-TW Evolutionary Report (L3)",
        "",
        "## Capability Heatmap (Failure Density)",
    ]
    
    if not heatmap:
        lines.append("No failures recorded. System is operating nominally.")
    else:
        for cat, count in sorted(heatmap.items(), key=lambda x: x[1], reverse=True):
            intensity = "🔥" * min(5, (count // 2) + 1)
            lines.append(f"- **{cat}**: {count} incidents {intensity}")
            
    lines.extend([
        "",
        "## Weak Area Detection",
        "Based on the heatmap, the following areas require systemic improvements:",
    ])
    
    critical_areas = [c for c, count in heatmap.items() if count >= 5]
    if critical_areas:
        for area in critical_areas:
            lines.append(f"- **{area}**: High failure rate. Recommend creating a dedicated Skill or adding specific Preflight Gate checks.")
    else:
        lines.append("- No critical weak areas detected at this time.")
        
    lines.extend([
        "",
        "## Meta-Learning & Alignment",
        "- [ ] Review AGENTS.md to ensure all patches align with core principles.",
        "- [ ] Check reflection ROI: Are we spending more time reflecting than executing?",
        ""
    ])
    
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        
    print(f"Generated L3 Evolution Report at {REPORT_FILE}")

def main():
    print("--- L3 Evolution Engine ---")
    
    logs = []
    if LOG_FILE.exists():
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        logs.append(json.loads(line))
                    except:
                        pass
                        
    heatmap = generate_heatmap(logs)
    generate_report(heatmap)

if __name__ == "__main__":
    main()

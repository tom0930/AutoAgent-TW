#!/usr/bin/env python3
"""
AutoAgent-TW Reflection Pattern Matcher (Phase 166: Wave 2)
===========================================================
L2 Strategic Pattern Matcher.
Analyzes reflection_log.jsonl to find frequent or similar failures
and decides whether they cross the dynamic threshold to warrant a patch.
"""

import json
import os
import sys
from pathlib import Path
from collections import defaultdict
from typing import List, Dict

WORKSPACE = Path(os.getcwd())
LOG_FILE = WORKSPACE / ".agent-state" / "reflection_log.jsonl"

# Dynamic thresholds based on category severity
THRESHOLDS = {
    "type_safety": 3,
    "prompt_gap": 3,
    "arch_flaw": 2,
    "security": 1,
    "resource_leak": 2,
    "default": 3
}

def load_logs() -> List[Dict]:
    """Load logs from episodic memory buffer."""
    logs = []
    if not LOG_FILE.exists():
        return logs
        
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                logs.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return logs

def detect_patterns(logs: List[Dict]) -> List[Dict]:
    """Detect frequent or critical patterns."""
    category_counts = defaultdict(list)
    
    for log in logs:
        for failure in log.get("failures", []):
            cat = failure.get("category", "default")
            category_counts[cat].append({
                "record_id": log["id"],
                "phase": log["phase"],
                "detail": failure.get("detail", "")
            })
            
    patterns_to_patch = []
    
    for cat, incidents in category_counts.items():
        threshold = THRESHOLDS.get(cat, THRESHOLDS["default"])
        if len(incidents) >= threshold:
            patterns_to_patch.append({
                "category": cat,
                "incident_count": len(incidents),
                "threshold": threshold,
                "samples": incidents[:3] # Include up to 3 samples for context
            })
            
    return patterns_to_patch

def main():
    print("--- L2 Pattern Matcher ---")
    logs = load_logs()
    print(f"Loaded {len(logs)} records from {LOG_FILE.name}")
    
    patterns = detect_patterns(logs)
    
    if not patterns:
        print("No patterns crossed the threshold. Archiving.")
        sys.exit(0)
        
    print(f"Found {len(patterns)} patterns requiring patches:")
    for p in patterns:
        print(f"  - [{p['category']}] Count: {p['incident_count']} (Threshold: {p['threshold']})")
        
    # In a real pipeline, this would trigger patch_generator.py
    # Here we just output the findings.
    
    # Save patterns to a temp file for patch generator to pick up
    out_file = WORKSPACE / ".agent-state" / "pending_patterns.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(patterns, f, ensure_ascii=False, indent=2)
        
    print(f"Saved pending patterns to {out_file.name}")

if __name__ == "__main__":
    main()

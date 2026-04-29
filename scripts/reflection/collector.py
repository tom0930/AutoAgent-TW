#!/usr/bin/env python3
"""
AutoAgent-TW Reflection Collector (Phase 166: Wave 1)
======================================================
L1 Tactical Reflection Data Collector.
Responsible for parsing QA and Review reports, and logging failures
into the episodic memory buffer (reflection_log.jsonl).
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(os.getcwd())
STATE_DIR = WORKSPACE / ".agent-state"
LOG_FILE = STATE_DIR / "reflection_log.jsonl"

def init_log():
    if not STATE_DIR.exists():
        STATE_DIR.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            pass

def parse_qa_report(phase: int) -> list:
    """Parses QA-REPORT.md to extract failures."""
    failures = []
    # Try to find the QA report for the phase
    planning_dir = WORKSPACE / ".planning" / "phases"
    if not planning_dir.exists():
        return failures
    
    report_paths = list(planning_dir.glob(f"{phase}-*/QA-REPORT.md"))
    if not report_paths:
        return failures
        
    target_report = report_paths[0]
    try:
        content = target_report.read_text(encoding="utf-8")
        # Simple extraction logic: look for lines starting with FAIL or - [FAIL]
        for line in content.splitlines():
            if "FAIL" in line.upper():
                failures.append({
                    "category": "qa_failure",
                    "detail": line.strip(),
                    "source": "QA-REPORT"
                })
    except Exception as e:
        print(f"Error reading QA report: {e}")
        
    return failures

def append_to_log(phase: int, failures: list, outcome: str = "PARTIAL_FAIL"):
    """Appends structured failure data to the reflection log."""
    init_log()
    
    if not failures:
        # No failures to log
        return

    timestamp = datetime.now().astimezone().isoformat()
    record_id = f"refl-{datetime.now().strftime('%Y%m%d%H%M%S')}-{phase}"
    
    record = {
        "id": record_id,
        "phase": phase,
        "timestamp": timestamp,
        "outcome": outcome,
        "failures": failures,
        "root_cause": "pending_analysis",
        "time_wasted_minutes": 0 # Default, can be enriched later
    }
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
        
    print(f"Logged {len(failures)} failures to {LOG_FILE.name}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python collector.py <phase_number>")
        sys.exit(1)
        
    try:
        phase = int(sys.argv[1])
    except ValueError:
        print("Error: Phase must be an integer.")
        sys.exit(1)
        
    failures = parse_qa_report(phase)
    if failures:
        append_to_log(phase, failures)
        print("Collector finished successfully.")
    else:
        print("No failures detected to collect.")

if __name__ == "__main__":
    main()

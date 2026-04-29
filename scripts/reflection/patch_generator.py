#!/usr/bin/env python3
"""
AutoAgent-TW Reflection Patch Generator (Phase 166: Wave 2)
===========================================================
L2 Strategic Patch Generator.
Takes patterns identified by pattern_matcher and uses meta-prompting
to generate structured patch proposals: {prompt_patch, rule_patch, expected_impact, risk_score}.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List

WORKSPACE = Path(os.getcwd())
PENDING_FILE = WORKSPACE / ".agent-state" / "pending_patterns.json"
PATCH_FILE = WORKSPACE / ".agent-state" / "proposed_patches.json"

def calculate_risk_score(category: str, detail: str) -> int:
    """Calculates risk score (1-10) based on category and detail."""
    if category == "security":
        return 9
    elif category == "arch_flaw":
        return 8
    elif "AGENTS.md" in detail or "core" in detail.lower():
        return 7
    elif category == "type_safety":
        return 3
    elif category == "prompt_gap":
        return 4
    return 5

def generate_patch(pattern: Dict) -> Dict:
    """Simulates LLM meta-prompting to generate a patch proposal."""
    # In a fully integrated system, this would call an LLM with a meta-prompt.
    # Here we simulate the output structure.
    
    category = pattern["category"]
    samples = pattern.get("samples", [])
    detail = samples[0]["detail"] if samples else "Unknown issue"
    
    risk_score = calculate_risk_score(category, detail)
    
    prompt_patch = f"Add explicit instruction to avoid {category} issues."
    rule_patch = None
    
    if risk_score > 6:
        rule_patch = f"Rule: Always double check {category} constraints."
        
    patch_proposal = {
        "id": f"patch-{category}-{len(samples)}",
        "category": category,
        "prompt_patch": prompt_patch,
        "rule_patch": rule_patch,
        "expected_impact": "Will reduce failure rate by addressing root cause.",
        "risk_score": risk_score,
        "status": "pending_safety_validation"
    }
    
    return patch_proposal

def main():
    print("--- L2 Patch Generator ---")
    
    if not PENDING_FILE.exists():
        print("No pending patterns found.")
        sys.exit(0)
        
    with open(PENDING_FILE, "r", encoding="utf-8") as f:
        patterns = json.load(f)
        
    if not patterns:
        print("Empty pattern list.")
        sys.exit(0)
        
    print(f"Generating patches for {len(patterns)} patterns...")
    
    proposed_patches = []
    for pattern in patterns:
        patch = generate_patch(pattern)
        proposed_patches.append(patch)
        print(f"  - Generated Patch [Risk: {patch['risk_score']}/10]: {patch['category']}")
        
    with open(PATCH_FILE, "w", encoding="utf-8") as f:
        json.dump(proposed_patches, f, ensure_ascii=False, indent=2)
        
    print(f"Saved {len(proposed_patches)} proposed patches to {PATCH_FILE.name}")
    
    # Clean up pending
    PENDING_FILE.unlink()

if __name__ == "__main__":
    main()

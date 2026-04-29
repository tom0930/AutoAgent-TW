#!/usr/bin/env python3
"""
AutoAgent-TW Reflection Safety Validator (Phase 166: Wave 3)
============================================================
Checks patch proposals for STRIDE threats and ensures they do not
modify critical system paths or escalate privileges.
"""

import json
import os
import sys
from pathlib import Path

WORKSPACE = Path(os.getcwd())
PATCH_FILE = WORKSPACE / ".agent-state" / "proposed_patches.json"
CRITICAL_PATHS = ["AGENTS.md", "risk-tiers.json", ".env", "src/core", "SECURITY.md"]

def validate_patch(patch: dict) -> bool:
    """Validates if a patch is safe to apply."""
    print(f"  [Safety] Validating patch '{patch['id']}'")
    
    # 1. Check for Critical Path modifications
    rule = patch.get("rule_patch", "")
    prompt = patch.get("prompt_patch", "")
    content = f"{rule} {prompt}".lower()
    
    for path in CRITICAL_PATHS:
        if path.lower() in content:
            print(f"  [Safety] [REJECTED] Patch attempts to reference/modify critical path '{path}'")
            return False
            
    # 2. Risk Score check (STRIDE heuristic)
    # E.g. we might reject if the patch mentions exec, subprocess, eval, etc.
    dangerous_keywords = ["eval(", "exec(", "subprocess", "rm -rf", "drop table"]
    for kw in dangerous_keywords:
        if kw in content:
            print(f"  [Safety] [REJECTED] Patch contains dangerous keyword '{kw}'")
            return False
            
    if patch.get("risk_score", 0) > 8:
        print("  [Safety] [WARN] High risk score detected. Will require strict HumanGate.")
        # We don't fail it here, but we mark it as needing strict human gate
        patch["requires_human"] = True
    else:
        patch["requires_human"] = False
        
    print("  [Safety] [OK] PASSED safety validation.")
    return True

def main():
    print("--- Safety Validator ---")
    
    if not PATCH_FILE.exists():
        print("No proposed patches to validate.")
        sys.exit(0)
        
    with open(PATCH_FILE, "r", encoding="utf-8") as f:
        patches = json.load(f)
        
    safe_patches = []
    
    for patch in patches:
        if validate_patch(patch):
            # If valid, it remains in pending_safety_validation but passed
            # Actually, let's just keep it in the list so Sandbox Runner can pick it up
            safe_patches.append(patch)
        else:
            print(f"Patch {patch['id']} was rejected by Safety Validator.")
            
    # Write back only safe patches
    with open(PATCH_FILE, "w", encoding="utf-8") as f:
        json.dump(safe_patches, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
AutoAgent-TW Skill Extractor (Phase 166: Wave 4)
================================================
Extracts reusable instructions from verified patches and adds them
to the Skill Library.
"""

import json
import os
import sys
from pathlib import Path

WORKSPACE = Path(os.getcwd())
VERIFIED_FILE = WORKSPACE / ".agent-state" / "verified_patches.json"
SKILL_DIR = WORKSPACE / "skills" / "auto_extracted"

def extract_skill(patch: dict):
    """Converts a verified patch into a minimal skill markdown."""
    if not SKILL_DIR.exists():
        SKILL_DIR.mkdir(parents=True, exist_ok=True)
        
    skill_id = patch.get("id", "unknown_skill")
    skill_file = SKILL_DIR / f"{skill_id}.md"
    
    content = f"""# Extracted Skill: {skill_id}
> Automatically extracted from reflection patch.

## Trigger/Category
- {patch.get('category')}

## Instruction
{patch.get('prompt_patch', 'No specific prompt instruction.')}

## Rule Constraint
{patch.get('rule_patch', 'No specific rule constraint.')}
"""
    with open(skill_file, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"  [Skill Extractor] Extracted skill to {skill_file.relative_to(WORKSPACE)}")

def main():
    print("--- Skill Extractor ---")
    
    if not VERIFIED_FILE.exists():
        print("No verified patches to extract.")
        sys.exit(0)
        
    with open(VERIFIED_FILE, "r", encoding="utf-8") as f:
        patches = json.load(f)
        
    extracted_count = 0
    for patch in patches:
        if patch.get("status") == "verified":
            extract_skill(patch)
            extracted_count += 1
            
    print(f"Extracted {extracted_count} skills from verified patches.")
    
    # We might choose to archive VERIFIED_FILE after processing, but for now we leave it.

if __name__ == "__main__":
    main()

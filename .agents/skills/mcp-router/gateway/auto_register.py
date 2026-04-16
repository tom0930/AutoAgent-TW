#!/usr/bin/env python3
import json
import os
from pathlib import Path

def auto_register():
    print("[MCP Router] Starting auto-registration of local skills...")
    
    # Path to the skills directory
    skills_root = Path("z:/autoagent-TW/.agents/skills")
    registry_path = skills_root / "mcp-router" / "config" / "registered_tools.json"
    
    tools = []
    
    # Scan for directories containing SKILL.md
    if skills_root.exists():
        for skill_dir in skills_root.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                skill_name = skill_dir.name
                if skill_name != "mcp-router":
                    tools.append({
                        "name": skill_name,
                        "path": str(skill_dir),
                        "status": "ready"
                    })
    
    # Save the registry
    with open(registry_path, "w", encoding="utf-8") as f:
        json.dump({"tools": tools}, f, indent=4)
    
    print(f"✅ Successfully registered {len(tools)} skills to MCP Router Gateway.")

if __name__ == "__main__":
    auto_register()

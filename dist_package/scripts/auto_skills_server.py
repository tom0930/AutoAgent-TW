import os
import json
from fastmcp import FastMCP
from typing import List, Optional
import pathlib

# Initialize FastMCP server
mcp = FastMCP("Auto Skills Engine")

# Path Configuration
DEFAULT_GLOBAL_SKILLS_DIR = os.path.expandvars(r"%USERPROFILE%\.gemini\antigravity\skills")
LIBRARY_DIR = os.path.expandvars(r"%USERPROFILE%\.gemini\antigravity\skills_library")
INDEX_PATH = os.path.join(DEFAULT_GLOBAL_SKILLS_DIR, "data", "skills_index.json")

def load_index():
    if not os.path.exists(INDEX_PATH):
        return []
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

@mcp.tool()
async def search_skills(query: str) -> str:
    """
    Search for skills in the 1500+ Antigravity library using keywords.
    
    Args:
        query: Search keywords
    """
    index = load_index()
    if not index:
        return "Error: Skills index not found. Please run 'python scripts/build_skills_index.py' first."
    
    query = query.lower()
    results = []
    
    for skill in index:
        if query in skill['name'].lower() or query in skill['description'].lower() or query in skill['id'].lower():
            results.append(skill)
            
    if not results:
        return f"No skills found matching '{query}' in the library."
    
    # Format top 10 results
    output = [f"Found {len(results)} skills matching '{query}':\n"]
    for s in results[:10]:
        output.append(f"- [{s['id']}] {s['name']}: {s['description']}")
    
    if len(results) > 10:
        output.append(f"\n... and {len(results) - 10} more. Use a more specific query if needed.")
        
    return "\n".join(output)

@mcp.tool()
async def get_skill_content(skill_id: str) -> str:
    """
    Retrieve the full SKILL.md content for a specific skill from the library.
    Use this to 'load' skill instructions without installing them.
    
    Args:
        skill_id: The ID of the skill (folder name)
    """
    skill_path = os.path.join(LIBRARY_DIR, skill_id, "SKILL.md")
    if not os.path.exists(skill_path):
        return f"Error: Skill '{skill_id}' not found in library at {skill_path}."
        
    with open(skill_path, 'r', encoding='utf-8') as f:
        return f.read()

@mcp.tool()
async def install_skill(skill_id: str) -> str:
    """
    Permanently activate a skill by moving it from the library to the active skills directory.
    
    Args:
        skill_id: The ID of the skill to install
    """
    src = os.path.join(LIBRARY_DIR, skill_id)
    dest = os.path.join(DEFAULT_GLOBAL_SKILLS_DIR, skill_id)
    
    if not os.path.exists(src):
        return f"Error: Skill '{skill_id}' not found in library."
        
    if os.path.exists(dest):
        return f"Skill '{skill_id}' is already installed and active."
    
    # Use powershell for robust directory copying on Windows
    import subprocess
    try:
        subprocess.run(["powershell", "-Command", f"Copy-Item '{src}' '{dest}' -Recurse -Force"], check=True)
        return f"Successfully installed and activated '{skill_id}'."
    except Exception as e:
        return f"Failed to install skill: {str(e)}"

@mcp.tool()
async def generate_skill(task_context: str, skill_name: str) -> str:
    """
    Automatically generate a new SKILL.md based on the current task context.
    
    Args:
        task_context: Description of the task/problem
        skill_name: Desired name for the new skill (should start with 'aa-' or your preferred prefix)
    """
    print(f"[Tip] Generating custom skill '{skill_name}'...")
    
    skill_content = f"""---
name: {skill_name}
description: Auto-generated skill for {task_context[:50]}...
---

# {skill_name}

## When to use
- {task_context}

## Steps
1. Analyze the context.
2. Execute the necessary actions.
"""
    
    skill_dir = os.path.join(DEFAULT_GLOBAL_SKILLS_DIR, skill_name)
    os.makedirs(skill_dir, exist_ok=True)
    
    with open(os.path.join(skill_dir, "SKILL.md"), "w", encoding="utf-8") as f:
        f.write(skill_content)
        
    return f"Custom skill '{skill_name}' generated at {skill_dir}"

if __name__ == "__main__":
    mcp.run()

import os
import json
from typing import Dict, Any, Optional
# pyrefly: ignore [missing-import]
from src.core.skill_manifest import SkillManifest

class SkillGeneratorEngine:
    """
    AutoSkills Dynamic Skill Generator (Phase 2 - Task 2.1).
    Orchestrates the creation of manifest.json, SKILL.md, and tests.
    """
    def __init__(self, output_base_dir: str = "temp/generated_skills"):
        self.output_base_dir = output_base_dir
        os.makedirs(self.output_base_dir, exist_ok=True)

    def generate_skill_package(self, intent: str, requirements: Optional[str] = None) -> Dict[str, Any]:
        """
        Main entry for generating a skill package.
        In production, this would call a LLM to generate content.
        Here we implement the structural orchestration.
        """
        # 1. Clean intent to folder name
        skill_name = intent.lower().replace(" ", "-")[:20]
        skill_dir = os.path.join(self.output_base_dir, skill_name)
        os.makedirs(skill_dir, exist_ok=True)
        os.makedirs(os.path.join(skill_dir, "tests"), exist_ok=True)
        os.makedirs(os.path.join(skill_dir, "scripts"), exist_ok=True)

        print(f"Generating Skill Package: '{skill_name}' for intent: '{intent}'")

        # 2. Mock Content Generation (Simulating LLM Output)
        # In actual use, we would send a prompt to produce these 3 files.
        
        # A. manifest.json
        # Automatically infer risk_level based on keywords
        risk = 1
        if any(w in intent.lower() for w in ["delete", "remove", "wipe"]): risk = 5
        elif any(w in intent.lower() for w in ["write", "exec", "system"]): risk = 4
        elif any(w in intent.lower() for w in ["read", "api", "network"]): risk = 3
        
        manifest = {
            "name": skill_name,
            "version": "1.0.0",
            "description": f"Automatically generated skill for: {intent}",
            "risk_level": risk,
            "permissions": {
                "tools": ["browser", "local_rag_read"] if "search" in intent.lower() else ["default"],
                "network": True if "api" in intent.lower() or "search" in intent.lower() else False
            },
            "entry": "SKILL.md",
            "auto_evolve": True
        }

        # B. SKILL.md (The Core Instruction)
        skill_md = f"""# {skill_name.capitalize()} Skill

## Description
{manifest['description']}

## How to use
This skill was generated based on the intent: "{intent}".
{requirements if requirements else "Follow standard tool calling patterns."}

## Examples
1. User: "{intent} example"
   Assistant: Calling related tools to fulfill "{intent}".
"""

        # C. tests/basic.json
        test_case = {
            "id": f"test-{skill_name}-001",
            "tool_call": {"name": manifest["permissions"]["tools"][0], "args": {"input": intent}},
            "expected": "*"
        }

        # 3. Write files
        try:
            with open(os.path.join(skill_dir, "manifest.json"), "w") as f:
                json.dump(manifest, f, indent=2)
            
            with open(os.path.join(skill_dir, "SKILL.md"), "w") as f:
                f.write(skill_md)
                
            with open(os.path.join(skill_dir, f"tests/basic.json"), "w") as f:
                json.dump([test_case], f, indent=2)
                
            return {
                "success": True,
                "skill_name": skill_name,
                "path": skill_dir,
                "manifest": manifest
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    print("Testing Skill Generator...")
    gen = SkillGeneratorEngine()
    
    # Example: Generating a Wikipedia search skill
    result = gen.generate_skill_package("Wikipedia Search API")
    print(f"Generation Result:\n{json.dumps(result, indent=2)}")

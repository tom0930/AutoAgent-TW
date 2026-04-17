import os
import json
from typing import List, Dict, Any, Optional
# pyrefly: ignore [missing-import]
from src.core.skill_manifest import SkillManifest

class SkillDiscoveryEngine:
    """
    AutoSkills Discovery Tool (Phase 2 - Task 1.2).
    Searches for skills locally and (mocked) remotely.
    """
    def __init__(self, workspace_dir: str = ".agents/skills"):
        self.workspace_dir = workspace_dir

    def search_local(self, intent: str) -> List[Dict[str, Any]]:
        """Search local skill directories for SKILL.md or manifest.json."""
        hits = []
        if not os.path.exists(self.workspace_dir):
            return []
            
        for skill_dir_name in os.listdir(self.workspace_dir):
            skill_path = os.path.join(self.workspace_dir, skill_dir_name)
            if not os.path.isdir(skill_path):
                continue
                
            manifest_file = os.path.join(skill_path, "manifest.json")
            if os.path.exists(manifest_file):
                try:
                    with open(manifest_file, "r") as f:
                        data = json.load(f)
                    # Use Pydantic to validate & default missing fields
                    manifest = SkillManifest(**data)
                    
                    # Intent check (Simple keyword match in name/description)
                    if intent.lower() in manifest.name.lower() or intent.lower() in manifest.description.lower():
                        hits.append({
                            "source": "local",
                            "name": manifest.name,
                            "version": manifest.version,
                            "description": manifest.description,
                            "risk_level": manifest.risk_level,
                            "permissions": manifest.permissions.model_dump()
                        })
                except Exception:
                    pass # Skip invalid manifests
                    
        return hits

    def search_remote_mock(self, intent: str) -> List[Dict[str, Any]]:
        """Mocked ClawHub API response for intent-based search."""
        # Simulated ClawHub hits for demo
        remote_catalog = [
            {
                "name": "selenium-browser-automation",
                "slug": "selenium-browser",
                "description": "Cross-platform browser automation with Selenium",
                "risk_level": 4,
                "permissions": {"gui": {"click": True}, "network": {"allow_domains": ["*"]}}
            },
            {
                "name": "exchange-rate-checker",
                "slug": "currency-plus",
                "description": "Fetch real-time currency conversion rates",
                "risk_level": 1,
                "permissions": {"network": {"allow_domains": ["api.exchangerate.host"]}}
            }
        ]
        
        # Simple match logic
        results = []
        for item in remote_catalog:
            # pyrefly: ignore [missing-attribute]
            if intent.lower() in item["name"].lower() or intent.lower() in item["description"].lower():
                item["source"] = "clawhub"
                results.append(item)
                
        return results[:3]

    def discover(self, intent: str) -> Dict[str, Any]:
        """Final Discovery aggregated results."""
        local = self.search_local(intent)
        remote = self.search_remote_mock(intent)
        
        all_hits = local + remote
        # Sort by relevance or source
        return {
            "intent": intent,
            "total_count": len(all_hits),
            "candidates": all_hits[:3] # Limit to top 3
        }

if __name__ == "__main__":
    print("Testing Skill Discovery Tool...")
    engine = SkillDiscoveryEngine()
    
    # Task: Looking for browser tools
    result = engine.discover("browser")
    print(f"Results for 'browser':\n{json.dumps(result, indent=2)}")

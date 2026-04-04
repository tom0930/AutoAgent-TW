import os
import json
import time
from typing import List, Dict, Any, Optional
from src.agents.skills.skill_metrics import SkillMetricsManager
from src.agents.tools.skills_generate import SkillGeneratorEngine
from src.core.skill_manifest import SkillManifest

class SkillEvolutionEngine:
    """
    AutoSkills Evolution Engine (Phase 2 - Task 3.2).
    Automates updates or re-generation of underperforming skills.
    """
    def __init__(self, 
                 skills_dir: str = ".agents/skills",
                 metrics_dir: str = ".agent-state/memory/skills"):
        self.skills_dir = skills_dir
        self.metrics_mgr = SkillMetricsManager(metrics_dir)
        self.generator = SkillGeneratorEngine()

    def run_evolution_cycle(self) -> List[Dict[str, Any]]:
        """
        Scans all skills, checks health, and triggers evolution for 
        low-performing ones with 'auto_evolve' enabled.
        """
        evolution_reports = []
        if not os.path.exists(self.skills_dir):
            return []

        for skill_name in os.listdir(self.skills_dir):
            skill_path = os.path.join(self.skills_dir, skill_name)
            if not os.path.isdir(skill_path):
                continue
                
            manifest_file = os.path.join(skill_path, "manifest.json")
            if not os.path.exists(manifest_file):
                continue
                
            try:
                with open(manifest_file, "r") as f:
                    manifest = SkillManifest(**json.load(f))
                
                # Check if evolution is requested
                if not manifest.auto_evolve:
                    continue
                    
                # Check health
                health = self.metrics_mgr.get_health_summary(skill_name)
                success_rate_val = float(health.get("success_rate", "100.0%").strip("%"))
                
                if success_rate_val < 85.0:
                    print(f"[{skill_name}] Low health detected ({success_rate_val}%). Triggering Evolution...")
                    report = self._evolve_skill(manifest, health)
                    evolution_reports.append(report)
                else:
                    print(f"[{skill_name}] Healthy ({success_rate_val}%). Skipping Evolution.")
                    
            except Exception as e:
                print(f"Error processing '{skill_name}': {str(e)}")

        return evolution_reports

    def _evolve_skill(self, manifest: SkillManifest, health: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tries to improve a skill by re-generating it with the error context.
        In a production scenario, this would include last failure logs.
        """
        intent = manifest.name.capitalize().replace("-", " ")
        # Add error context if available
        # In actual use, we'd feed this into the generator
        
        result = self.generator.generate_skill_package(intent, requirements=f"Improvement needed. Current status: {health.get('status')}")
        
        return {
            "skill": manifest.name,
            "old_success_rate": health.get("success_rate"),
            "evolution_result": "success" if result["success"] else "failure",
            "new_path": result.get("path"),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

if __name__ == "__main__":
    print("Testing Skill Evolution Engine...")
    # Mock some data for evolution test
    skill_dir = ".agents/skills/browser-search"
    os.makedirs(skill_dir, exist_ok=True)
    with open(os.path.join(skill_dir, "manifest.json"), "w") as f:
        json.dump({
            "name": "browser-search",
            "version": "1.0",
            "description": "Mock Skill",
            "auto_evolve": True,
            "risk_level": 3
        }, f)
    
    # Mock low health (50% success rate)
    metrics_mgr = SkillMetricsManager()
    metrics_mgr.record_run("browser-search", success=True, latency=1.0)
    metrics_mgr.record_run("browser-search", success=False, latency=1.5, error="Failed to find element")
    
    evo_engine = SkillEvolutionEngine()
    reports = evo_engine.run_evolution_cycle()
    print(f"\nEvolution Cycle Complete. Reports:\n{json.dumps(reports, indent=2)}")

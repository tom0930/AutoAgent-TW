import os
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime

class SkillMetricsManager:
    """
    AutoSkills Health Metrics Collector (Phase 2 - Task 3.1).
    Tracks success/failure rates, latency, and usage counts.
    """
    def __init__(self, metrics_base_dir: str = ".agent-state/memory/skills"):
        self.metrics_base_dir = metrics_base_dir
        os.makedirs(self.metrics_base_dir, exist_ok=True)

    def _get_metrics_path(self, skill_name: str) -> str:
        skill_dir = os.path.join(self.metrics_base_dir, skill_name)
        os.makedirs(skill_dir, exist_ok=True)
        return os.path.join(skill_dir, "metrics.json")

    def load_metrics(self, skill_name: str) -> Dict[str, Any]:
        path = self._get_metrics_path(skill_name)
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "skill_name": skill_name,
            "total_runs": 0,
            "success_count": 0,
            "failure_count": 0,
            "avg_latency": 0.0,
            "last_run": None,
            "history": []
        }

    def record_run(self, skill_name: str, success: bool, latency: float, error: Optional[str] = None):
        """Records a single execution of a skill."""
        metrics = self.load_metrics(skill_name)
        
        metrics["total_runs"] += 1
        if success:
            metrics["success_count"] += 1
        else:
            metrics["failure_count"] += 1
            
        # Cumulative average calculation
        n = metrics["total_runs"]
        old_avg = metrics["avg_latency"]
        metrics["avg_latency"] = ((old_avg * (n - 1)) + latency) / n
        
        metrics["last_run"] = datetime.now().isoformat()
        
        # Keep a small log of the last 10 runs
        entry = {
            "timestamp": metrics["last_run"],
            "success": success,
            "latency": latency,
            "error": error
        }
        metrics["history"] = ([entry] + metrics["history"])[:10]
        
        # Persist
        path = self._get_metrics_path(skill_name)
        with open(path, "w") as f:
            json.dump(metrics, f, indent=2)

    def get_health_summary(self, skill_name: str) -> Dict[str, Any]:
        """Calculates success rate and provides triage suggestions."""
        metrics = self.load_metrics(skill_name)
        
        if metrics["total_runs"] == 0:
            return {"status": "unknown", "message": "No data yet."}
            
        success_rate = (metrics["success_count"] / metrics["total_runs"]) * 100
        
        status = "healthy"
        suggestion = "Keep as is."
        
        if success_rate < 50:
            status = "critical"
            suggestion = "Urgent regeneration or manual fix required."
        elif success_rate < 85:
            status = "warning"
            suggestion = "Consider evolution (Task 3.2)."
            
        return {
            "skill_name": skill_name,
            "status": status,
            "success_rate": f"{success_rate:.1f}%",
            "avg_latency": f"{metrics['avg_latency']:.2f}s",
            "total_runs": metrics["total_runs"],
            "suggestion": suggestion
        }

if __name__ == "__main__":
    print("Testing Skill Metrics Manager...")
    mgr = SkillMetricsManager()
    
    skill = "test-browser-skill"
    # Record some mock runs
    mgr.record_run(skill, success=True, latency=1.2)
    mgr.record_run(skill, success=False, latency=4.5, error="Timeout")
    mgr.record_run(skill, success=True, latency=0.8)
    
    summary = mgr.get_health_summary(skill)
    print(f"\nHealth Summary for '{skill}':\n{json.dumps(summary, indent=2)}")

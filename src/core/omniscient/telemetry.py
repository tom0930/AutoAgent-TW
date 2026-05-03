import time
import logging
from typing import Dict, Any, List
from collections import defaultdict

logger = logging.getLogger("Omniscient.Telemetry")

class TelemetryManager:
    """
    Observability System for Multi-Agent Operations (Phase 171 v2.1).
    Tracks Squad Success, Token Costs, and Latency.
    """
    def __init__(self):
        self.metrics = {
            "squad_success": {"success": 0, "fail": 0},
            "token_usage": defaultdict(int), # Role -> total_tokens
            "intervention_latency": [],      # List of float (seconds)
            "user_feedback_score": 1.0
        }
        self.start_times = {}

    def record_squad_result(self, squad_id: str, success: bool):
        key = "success" if success else "fail"
        self.metrics["squad_success"][key] += 1
        logger.info(f"Telemetry: Squad {squad_id} result={key}")

    def record_token_usage(self, role: str, tokens: int):
        self.metrics["token_usage"][role] += tokens

    def record_intervention_start(self, suggestion_id: str):
        self.start_times[suggestion_id] = time.time()

    def record_intervention_end(self, suggestion_id: str):
        if suggestion_id in self.start_times:
            latency = time.time() - self.start_times.pop(suggestion_id)
            self.metrics["intervention_latency"].append(latency)

    def get_summary(self) -> Dict[str, Any]:
        """Aggregates metrics for the dashboard."""
        s = self.metrics["squad_success"]
        total_squads = s["success"] + s["fail"]
        success_rate = (s["success"] / total_squads) if total_squads > 0 else 1.0
        
        avg_latency = (sum(self.metrics["intervention_latency"]) / len(self.metrics["intervention_latency"])) if self.metrics["intervention_latency"] else 0.0
        
        return {
            "success_rate": round(success_rate * 100, 1),
            "total_tokens": sum(self.metrics["token_usage"].values()),
            "token_by_role": dict(self.metrics["token_usage"]),
            "avg_latency_ms": round(avg_latency * 1000, 2),
            "active_squad_count": total_squads
        }

# Singleton Instance
telemetry = TelemetryManager()

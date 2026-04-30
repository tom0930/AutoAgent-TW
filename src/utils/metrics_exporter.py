import json
import time
import os
from typing import Dict, Any

class MetricsExporter:
    """
    Exports CI execution metrics to a structured JSON file.
    Used for performance monitoring and baseline tracking.
    """
    def __init__(self, output_path: str = ".agent-state/ci_metrics.json"):
        self.output_path = output_path
        self.start_time = time.time()
        self._metrics: Dict[str, Any] = {}

    def record_stage(self, stage_name: str, duration: float):
        self._metrics[f"stage_{stage_name}_sec"] = duration

    def finalize(self, exit_code: int, tokens_used: int = 0):
        total_duration = time.time() - self.start_time
        self._metrics["total_duration_sec"] = total_duration
        self._metrics["exit_code"] = exit_code
        self._metrics["tokens_used"] = tokens_used
        self._metrics["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, "w") as f:
            json.dump(self._metrics, f, indent=2)
            
        print(f"[MetricsExporter] CI metrics exported to {self.output_path}")

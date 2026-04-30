import os
import json
from src.utils.metrics_exporter import MetricsExporter

def test_metrics_exporter_serialization():
    temp_path = "tests/temp_metrics.json"
    exporter = MetricsExporter(output_path=temp_path)
    
    exporter.record_stage("planning", 1.5)
    exporter.finalize(exit_code=0, tokens_used=500)
    
    assert os.path.exists(temp_path)
    
    with open(temp_path, "r") as f:
        data = json.load(f)
        
    assert data["exit_code"] == 0
    assert data["tokens_used"] == 500
    assert data["stage_planning_sec"] == 1.5
    assert "total_duration_sec" in data
    
    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)

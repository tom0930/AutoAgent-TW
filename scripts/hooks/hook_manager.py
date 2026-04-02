import json
import os
from pathlib import Path

# Add project root to sys.path if not present (simplified for now)
import sys
project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.predictor.context_tracker import ContextTracker
from scripts.predictor.command_predictor import CommandPredictor

class HookManager:
    """
    攔截系統事件並觸發對應行為 (包括預測分析)
    """
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.tracker = ContextTracker(project_root)
        self.predictor = CommandPredictor()
        
        # Save predictions somewhere the dashboard can read
        self.predictions_file = Path(project_root) / ".agent-state" / "predictions.json"

    def trigger(self, event_name: str, event_data: dict = None):
        """觸發指定的系統事件"""
        print(f"[HookManager] Event triggered: {event_name}")
        
        # Track the event
        if event_name == "PostToolUse":
            if event_data and "file_path" in event_data:
                self.tracker.track_file_change(event_data["file_path"])
        elif event_name == "git.post-commit":
            self.tracker.track_git_event("post-commit", event_data or {})
            
        # After any state change, run predictor
        self.run_prediction_cycle()

    def run_prediction_cycle(self):
        """執行一次預測週期並儲存結果"""
        try:
            ctx = self.tracker.get_current_context()
            predictions = self.predictor.predict(ctx)
            
            # Write out to predictions.json for dashboard
            with open(self.predictions_file, "w", encoding="utf-8") as f:
                json.dump(predictions, f, indent=2, ensure_ascii=False)
                
            print(f"[HookManager] Generated {len(predictions)} predictions.")
        except Exception as e:
            print(f"[HookManager] Failed to run prediction cycle: {e}")

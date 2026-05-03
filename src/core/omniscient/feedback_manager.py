import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("Omniscient.Feedback")

class FeedbackManager:
    """
    Manages user feedback (Thumbs Up/Down) for AI suggestions (Phase 171 v2.1).
    Persistent storage used for online learning/sensitivity adjustment.
    """
    def __init__(self, storage_path: str = ".agent-state/omniscient/feedback.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.feedback_log: List[Dict[str, Any]] = self._load()

    def record_feedback(self, suggestion_id: str, is_positive: bool, context: Optional[Dict[str, Any]] = None):
        """Records a 👍 or 👎."""
        entry = {
            "id": suggestion_id,
            "positive": is_positive,
            "timestamp": time.time(),
            "context": context or {}
        }
        self.feedback_log.append(entry)
        self._save()
        logger.info(f"Feedback Recorded: {'👍' if is_positive else '👎'} for {suggestion_id}")

    def get_performance_metrics(self) -> Dict[str, float]:
        """Calculates user satisfaction metrics."""
        if not self.feedback_log:
            return {"satisfaction_score": 1.0}
        
        positives = sum(1 for f in self.feedback_log if f["positive"])
        score = positives / len(self.feedback_log)
        return {
            "satisfaction_score": round(score, 2),
            "total_entries": len(self.feedback_log)
        }

    def _load(self) -> List[Dict[str, Any]]:
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load feedback: {e}")
        return []

    def _save(self):
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self.feedback_log, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save feedback: {e}")

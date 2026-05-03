import logging
import time
from typing import Dict, Any, List
from .core import OmniscientAgentCore
from .feedback_manager import FeedbackManager

logger = logging.getLogger("Omniscient.SuggestionEngine")

class SuggestionEngine:
    """
    High-level engine to generate context-aware, evidence-linked suggestions (Phase 171 v2.1).
    """
    def __init__(self, core: OmniscientAgentCore, feedback: FeedbackManager):
        self.core = core
        self.feedback = feedback

    def analyze_workspace_crisis(self, error_report: str) -> Dict[str, Any]:
        """
        Deep analysis of a 'CRISIS' event.
        Returns a high-confidence suggestion with evidence.
        """
        # In a real scenario, this would call LLM/Opus
        # We mock the evidence linking here
        suggestion = {
            "suggestion_id": f"sug-{int(time.time())}",
            "title": "🔴 關鍵編譯失敗診斷",
            "content": f"偵測到相依性循環引用。錯誤點：{error_report[:50]}...",
            "action": "建議執行 /aa-fix 並套用 'Refactor Dependency' 策略",
            "evidence": [
                {"type": "lint", "file": "src/core/main.py", "line": 42},
                {"type": "history", "description": "Phase 168 曾出現類似循環"}
            ],
            "severity": "high"
        }
        return suggestion

    def get_sensitivity_adjustment(self) -> float:
        """
        Calculates how 'annoying' the AI should be based on feedback.
        """
        metrics = self.feedback.get_performance_metrics()
        score = metrics["satisfaction_score"]
        
        # If score is low, reduce sensitivity (Passive more often)
        if score < 0.5:
            return 0.5 # 50% less likely to be proactive
        return 1.0

    def run_l0_scan(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """
        Zero-cost (L0) scanner using regex/rules (Phase 171 v2.1).
        Detects code smells instantly without LLM calls.
        """
        suggestions = []
        
        # Rule 1: Complexity Check (File Length)
        if len(content.splitlines()) > 500:
            suggestions.append({
                "title": "📏 文件過長建議",
                "content": f"檔案 '{file_path}' 超過 500 行，建議拆分為更小的模組以提升可維護性。",
                "severity": "low",
                "type": "refactor"
            })

        # Rule 2: Security Check (Hardcoded Secrets - Simple)
        import re
        secret_patterns = [r'api_key\s*=\s*["\'][a-zA-Z0-9_]{20,}["\']', r'password\s*=\s*["\'].+["\']']
        for pattern in secret_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                suggestions.append({
                    "title": "🔒 潛在密鑰洩漏",
                    "content": "偵測到疑似硬編碼的 API Key 或密碼，建議使用 .env 或 Secret Manager。",
                    "severity": "high",
                    "type": "security"
                })
        
        return suggestions

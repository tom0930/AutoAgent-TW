import json

class CommandPredictor:
    """
    根據當前開發上下文，預測下一步最可能需要執行的指令
    """
    PREDICTION_RULES = [
        {
            "condition": lambda ctx: ctx.get("last_action") == "file_change" or bool(ctx.get("files_changed")),
            "suggestion": "Run tests / QA to verify changes",
            "command": "/aa-qa",
            "confidence": 0.9,
            "reason": "Files were modified recently."
        },
        {
            "condition": lambda ctx: ctx.get("git_status") == "post-commit" or (ctx.get("last_command", {}).get("command", "").startswith("git commit")),
            "suggestion": "Push changes & ship",
            "command": "/aa-ship",
            "confidence": 0.85,
            "reason": "Clean working tree after commit."
        },
        {
            "condition": lambda ctx: ctx.get("last_command", {}).get("result") == "fail",
            "suggestion": "Auto-fix the failing step",
            "command": "/aa-fix",
            "confidence": 0.95,
            "reason": "Previous command failed."
        },
        {
            "condition": lambda ctx: ctx.get("last_action") == "init",
            "suggestion": "Start planning the next phase",
            "command": "/aa-plan",
            "confidence": 0.8,
            "reason": "Project is idle or just initialized."
        }
    ]

    def predict(self, context: dict) -> list[dict]:
        """
        根據給定的 context (dict) 評估並回傳推薦清單
        回傳格式: [{"suggestion", "command", "confidence", "reason"}, ...]
        """
        predictions = []
        try:
            print(f"[PREDICTOR] Analyzing context: {context.get('last_action')}")
            for rule in self.PREDICTION_RULES:
                if rule["condition"](context):
                    predictions.append({
                        "suggestion": rule["suggestion"],
                        "command": rule["command"],
                        "confidence": rule["confidence"],
                        "reason": rule["reason"]
                    })
            
            # Sort by confidence descending
            predictions.sort(key=lambda x: x["confidence"], reverse=True)
            return predictions[:3]  # Return top 3
        except Exception as e:
            print(f"[PREDICTOR] Error during prediction: {e}")
            return []

    def render_suggestions(self, predictions: list[dict]) -> str:
        """渲染為終端機可顯示的建議列表格式"""
        if not predictions:
            return "No suggestions available."
        
        output = "💡 Suggested Next Actions:\n"
        for idx, p in enumerate(predictions, 1):
            output += f"  [{idx}] {p['suggestion']} -> {p['command']} (Confidence: {p['confidence']})\n"
        return output

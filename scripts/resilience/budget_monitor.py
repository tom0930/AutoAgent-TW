"""
Cost & Token Monitoring + Human In The Loop (Phase 4 & Phase 5)
監控預算：防止 Agent 在修復迴圈中耗費過多。
強行中斷：達到上限或遇到 FATAL 級別錯誤時，阻斷執行，透過 `line_notifier` 發送等待訊號給人工。
"""

import json
from pathlib import Path
import logging
import sys
import os

# 引用現有的 Line Notifier 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.agents', 'skills', 'status-notifier', 'scripts')))
import line_notifier

logger = logging.getLogger("resilience")

class BudgetMonitor:
    def __init__(self, daily_limit_usd: float = 5.0, task_limit_usd: float = 1.0):
        self.daily_limit_usd = daily_limit_usd
        self.task_limit_usd = task_limit_usd
        self.state_file = Path(".agent-state/budget.json")
        self._ensure_state_file()
        
    def _ensure_state_file(self):
        if not self.state_file.exists():
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump({"daily_usage": 0.0, "current_task": 0.0}, f)
                
    def _read_state(self) -> dict:
        with open(self.state_file, "r", encoding="utf-8") as f:
            return json.load(f)
            
    def _write_state(self, state: dict):
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4)
            
    def add_cost(self, usd_cost: float):
        state = self._read_state()
        state["daily_usage"] += usd_cost
        state["current_task"] += usd_cost
        
        # 觸發警告?
        if state["current_task"] > self.task_limit_usd:
            logger.error("🛑 任務預算已耗盡。轉為 FATAL。")
            self._write_state(state)
            self._trigger_human_intervention(f"⚠️ 個別任務預算超支！\n已消耗: ${state['current_task']:.2f}")
            raise Exception("BUDGET EXCEEDED")
            
        self._write_state(state)
        
    def _trigger_human_intervention(self, reason: str):
        """
        Phase 5: 致命錯誤人工介入流
        發生無法處理的例外或預算用盡，直接向 LINE 告警並等待（概念上停止執行）。
        """
        msg = f"🛑 【AutoAgent-TW 執行暫停】\n" \
              f"原因: {reason}\n" \
              f"請手動檢查 Agent 日誌或到儀表板介入處理。"
        try:
            line_notifier.send_line_notification(msg)
            logger.info("已發送人工介入請求 (LINE)。")
        except Exception:
            logger.error("無法發送 LINE 告警。")

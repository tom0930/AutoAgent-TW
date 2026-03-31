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
    def __init__(self, daily_char_limit: int = 1_000_000, task_char_limit: int = 200_000):
        self.daily_char_limit = daily_char_limit
        self.task_char_limit = task_char_limit
        self.state_file = Path(".agent-state/budget.json")
        self._ensure_state_file()
        
    def _ensure_state_file(self):
        if not self.state_file.exists():
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, "w", encoding="utf-8") as f:
                # 使用字元數 (Estimated Characters) 而非 USD
                json.dump({
                    "daily_chars": 0, 
                    "current_task_chars": 0,
                    "last_outputs": [] # 用於偵測重複動作
                }, f)
                
    def _read_state(self) -> dict:
        with open(self.state_file, "r", encoding="utf-8") as f:
            return json.load(f)
            
    def _write_state(self, state: dict):
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4, ensure_ascii=False)
            
    def record_usage(self, input_text: str, output_text: str):
        """
        [Phase 4] 字符估計監控
        由於 Antigravity IDE 暫時無法抓取實體 Token，我們計算傳輸字元數作為替代指標。
        """
        state = self._read_state()
        usage = len(input_text) + len(output_text)
        
        state["daily_chars"] += usage
        state["current_task_chars"] += usage
        
        # 異常偵測：記錄最後 3 次輸出，若完全相同則視為死循環
        state["last_outputs"].append(output_text[:500]) # 僅記錄摘要避免檔案過大
        if len(state["last_outputs"]) > 3:
            state["last_outputs"].pop(0)
            
        # 偵測重複行為 (Loop Detection)
        if len(state["last_outputs"]) == 3 and all(x == state["last_outputs"][0] for x in state["last_outputs"]):
            self._write_state(state)
            self._trigger_human_intervention("🔄 偵測到重複性『死循環』動作！Agent 可能正在打轉。")
            raise Exception("LOOP DETECTED")

        # 觸發預算警告
        if state["current_task_chars"] > self.task_char_limit:
            logger.error(f"🛑 任務字符預算已耗盡 ({state['current_task_chars']} chars)。轉為 FATAL。")
            self._write_state(state)
            self._trigger_human_intervention(f"⚠️ 個別任務消耗過大！\n預估消耗: {state['current_task_chars']} 字元 (約 {state['current_task_chars']//4} Tokens)")
            raise Exception("BUDGET EXCEEDED")
            
        self._write_state(state)
        
    def _trigger_human_intervention(self, reason: str):
        """
        [Phase 5] 致命錯誤人工介入流
        發送 LINE 通知並暫停任務。
        """
        msg = f"🛑 【AutoAgent-TW 執行暫停】\n" \
              f"原因: {reason}\n" \
              f"執行檔: {sys.argv[0]}\n" \
              f"請檢查儀表板或終端機以介入處理。"
        try:
            line_notifier.send_line_notification(msg)
            logger.info("已發送人工介入請求 (LINE)。")
        except Exception:
            logger.error("無法發送 LINE 告警（網路或權限問題）。")

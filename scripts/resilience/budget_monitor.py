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
                json.dump({
                    "daily_chars": 0, 
                    "current_task_chars": 0,
                    "total_calls": 0,
                    "retry_calls": 0,
                    "phase_usage": {}, # e.g. {"1": {"chars": 5000, "retries": 2}}
                    "last_outputs": [] 
                }, f)
                
    def _read_state(self) -> dict:
        with open(self.state_file, "r", encoding="utf-8") as f:
            return json.load(f)
            
    def _write_state(self, state: dict):
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4, ensure_ascii=False)
            
    def record_usage(self, input_text: str, output_text: str, is_retry: bool = False):
        """
        記錄字元數與重試狀況。
        """
        state = self._read_state()
        usage = len(input_text) + len(output_text)
        
        state["daily_chars"] += usage
        state["current_task_chars"] += usage
        state["total_calls"] = state.get("total_calls", 0) + 1
        if is_retry:
            state["retry_calls"] = state.get("retry_calls", 0) + 1
        
        # 取得當前 Phase
        current_phase = "0"
        try:
            status_file = Path(".agent-state/status_state.json")
            if status_file.exists():
                with open(status_file, "r", encoding="utf-8") as fs:
                    status_data = json.load(fs)
                    current_phase = str(status_data.get("phase_num", "0"))
        except: pass
        
        # 更新 Phase 統計
        if "phase_usage" not in state: state["phase_usage"] = {}
        if current_phase not in state["phase_usage"]:
            state["phase_usage"][current_phase] = {"chars": 0, "retries": 0, "calls": 0}
            
        phase_stats = state["phase_usage"][current_phase]
        phase_stats["chars"] += usage
        phase_stats["calls"] += 1
        if is_retry:
            phase_stats["retries"] += 1
        
        # 異常偵測 (Loop Detection)
        state["last_outputs"].append(output_text[:500])
        if len(state["last_outputs"]) > 3:
            state["last_outputs"].pop(0)
            
        if len(state["last_outputs"]) == 3 and all(x == state["last_outputs"][0] for x in state["last_outputs"]):
            self._write_state(state)
            self._trigger_human_intervention("LOOP DETECTED: Agent is repeating exactly the same output.")
            raise Exception("LOOP DETECTED")

        if state["current_task_chars"] > self.task_char_limit:
            self._write_state(state)
            self._trigger_human_intervention(f"BUDGET EXCEEDED: {state['current_task_chars']} chars")
            raise Exception("BUDGET EXCEEDED")
            
        self._write_state(state)

    def get_phase_report(self) -> str:
        """
        統計各 Phase 佔比，並抓出最高者，包含重試率。
        """
        state = self._read_state()
        usage_map = state.get("phase_usage", {})
        if not usage_map: return "No data available."
        
        total_chars = sum(p["chars"] for p in usage_map.values())
        total_retries = sum(p["retries"] for p in usage_map.values())
        total_calls = sum(p["calls"] for p in usage_map.values())

        report = ["\n[Resilience & Usage Report v1.7.0]"]
        max_phase = "None"
        max_val = -1
        
        for p, stats in sorted(usage_map.items()):
            val = stats["chars"]
            percent = (val / total_chars) * 100 if total_chars > 0 else 0
            retry_rate = (stats["retries"] / stats["calls"]) * 100 if stats["calls"] > 0 else 0
            
            if val > max_val:
                max_val = val
                max_phase = p
            
            report.append(f"Phase {p}: {val} chars ({percent:.1f}%) | Retries: {stats['retries']} ({retry_rate:.1f}%)")
            
        report.append(f"\n🏆 Total Resource: {total_chars} chars across {total_calls} calls")
        report.append(f"🔄 Global Reliability: {total_retries} Retries total")
        report.append(f"🚀 Usage Leader: Phase {max_phase} (Peak consumption)")
        return "\n".join(report)
        
    def _trigger_human_intervention(self, reason: str):
        """
        [Phase 5] 致命錯誤介入
        1. 更新 Dashboard 為 FAIL 狀態（變紅）
        2. 輸出 ANSI 紅色警告至終端機
        3. 發送 LINE 通知
        """
        # 1. 更新 Dashboard (直接修改 JSON 確保最快反應)
        try:
            state_dir = Path(".agent-state")
            state_file = state_dir / "status_state.json"
            if state_file.exists():
                with open(state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data["status"] = "fail"
                data["current_task"] = f"🛑 FATAL: {reason}"
                with open(state_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception: pass

        # 2. 終端機高亮度警告 (ANSI Red)
        red_start = "\033[91m\033[1m"
        reset = "\033[0m"
        print(f"\n{red_start}============================================================{reset}")
        print(f"{red_start}!! AUTOAGENT-TW FATAL ERROR !!{reset}")
        print(f"{red_start}REASON: {reason}{reset}")
        print(f"{red_start}============================================================{reset}\n")

        # 3. LINE 通知
        msg = f"! [AutoAgent-TW FATAL] !\nReason: {reason}\nPlease check Dashboard or Terminal."
        try:
            line_notifier.send_line_notification(msg)
        except Exception:
            logger.error("無法發送 LINE 告警。")

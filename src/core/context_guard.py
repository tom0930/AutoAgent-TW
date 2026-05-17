"""
AutoAgent-TW Context Guard & Safe Shell Interceptor
==================================================
功能：平台級上下文上限防衛、危險 Shell 靜態分析與 Mode B 攔截、Handoff 狀態簽署。
版本：v1.0.0
"""

import os
import re
import sys
import json
import time
import hmac
import hashlib
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List, Tuple

@dataclass
class CommandAnalysis:
    """SafeShell 分析結果"""
    safe: bool
    risk_level: str          # "safe", "caution", "dangerous", "blocked"
    original_cmd: str
    suggestion: str          # 人類可讀建議
    python_equivalent: str   # Python 替代程式碼
    requires_confirm: bool   # True = 需要用戶確認

# 危險指令識別規則與正則表達式
DANGEROUS_PATTERNS: List[Tuple[str, str, str]] = [
    (r"rm\s+-rf\s+/", "blocked", "嘗試刪除根目錄，此操作被完全禁止"),
    (r"Remove-Item.*\\\*", "dangerous", "萬用字元刪除，極易導致誤刪檔案"),
    (r"del\s+/[QqSs]", "dangerous", "使用 Windows cmd 批次刪除語法在 PowerShell 中不可靠"),
    (r";\s*rm\b|;\s*del\b", "dangerous", "鏈式刪除指令，可能導致非預期的刪除行為"),
    (r"&&", "caution", "PowerShell 不支援 && 語法，請改用分號 ';' 或管道字元"),
    (r"format\s+[A-Z]:", "blocked", "嘗試格式化系統磁碟槽，此操作被完全禁止"),
    (r"drop\s+table", "blocked", "嘗試直接刪除資料庫表，此操作被完全禁止"),
]

# 安全替代方案對照表
SAFE_ALTERNATIVES = {
    "mv": "shutil.move(src, dst)",
    "move": "shutil.move(src, dst)",
    "rm": "Path(target).unlink() / shutil.rmtree(target)",
    "del": "Path(target).unlink()",
    "mkdir": "Path(target).mkdir(parents=True, exist_ok=True)",
    "cp": "shutil.copy2(src, dst)",
    "copy": "shutil.copy2(src, dst)",
}

class ContextGuard:
    """Platform-level context budget enforcement & execution safety."""
    
    def __init__(self, context_limit: int = 128_000, 
                 warn_ratio: float = 0.70, 
                 critical_ratio: float = 0.85,
                 secret_key: bytes = b"autoagent-tw-context-guard-secret-key-2026"):
        self.context_limit = context_limit
        self.warn_ratio = warn_ratio
        self.critical_ratio = critical_ratio
        self.secret_key = secret_key
        
        self._accumulated_tokens = 0
        self._tool_call_log: List[Dict[str, Any]] = []
        
    def estimate_tokens(self, content: str) -> int:
        """高精度且支援多語言（中英混合）的啟發式 Token 估計演算法"""
        tokens = 0.0
        for char in content:
            # ASCII 字元（英文、符號、空格）：約 4 字元 = 1 token
            if ord(char) < 128:
                tokens += 0.25
            # 非 ASCII 字元（中文、CJK 字元）：1 字元 ≈ 1.5 tokens
            else:
                tokens += 1.5
        return int(tokens)
        
    def track(self, tool_name: str, content_size: int) -> int:
        """追蹤並累加 Token 用量，處理視覺工具乘數"""
        tokens = content_size // 4  # 預設估算
        
        # 視覺工具（如 view_file 圖片）有更高的 token 成本
        if tool_name in ("view_file", "view_image") and content_size > 10000:
            tokens = max(tokens, 3000)  # 圖片單次至少 3000 tokens
            
        self._accumulated_tokens += tokens
        self._tool_call_log.append({
            "ts": time.time(),
            "tool": tool_name,
            "tokens": tokens,
            "cumulative": self._accumulated_tokens
        })
        return tokens
        
    def get_usage(self) -> Dict[str, Any]:
        """取得目前 Token 使用量與狀態指標"""
        ratio = self._accumulated_tokens / self.context_limit if self.context_limit > 0 else 0.0
        level = "safe"
        if ratio >= self.critical_ratio:
            level = "critical"
        elif ratio >= self.warn_ratio:
            level = "warn"
            
        return {
            "tokens": self._accumulated_tokens,
            "limit": self.context_limit,
            "ratio": ratio,
            "level": level
        }
        
    def should_warn(self) -> bool:
        """是否達到警告閾值 (70%)"""
        return self.get_usage()["level"] in ("warn", "critical")
        
    def should_force_stop(self) -> bool:
        """是否達到強制停止閾值 (85%)"""
        return self.get_usage()["level"] == "critical"
        
    def reset(self) -> None:
        """在新對話或重置時清空累計數"""
        self._accumulated_tokens = 0
        self._tool_call_log.clear()
        
    # === Safe Shell ===
    def analyze_command(self, cmd: str) -> CommandAnalysis:
        """靜態語法規則分析，對 Shell 指令進行安全性分級並提供替代代碼"""
        cmd_stripped = cmd.strip()
        
        # 規則匹配
        for pattern, risk, desc in DANGEROUS_PATTERNS:
            if re.search(pattern, cmd_stripped, re.IGNORECASE):
                # blocked 指令直接禁止，不提供建議替代
                requires_confirm = (risk != "blocked")
                
                # 推導 Python 替代方案
                python_eq = ""
                for key, val in SAFE_ALTERNATIVES.items():
                    if key in cmd_stripped.lower():
                        python_eq = val
                        break
                        
                return CommandAnalysis(
                    safe=False,
                    risk_level=risk,
                    original_cmd=cmd_stripped,
                    suggestion=f"發現潛在風險操作: {desc} ({risk})",
                    python_equivalent=python_eq,
                    requires_confirm=requires_confirm
                )
                
        # 安全指令
        return CommandAnalysis(
            safe=True,
            risk_level="safe",
            original_cmd=cmd_stripped,
            suggestion="此指令通過安全靜態規則過濾",
            python_equivalent="",
            requires_confirm=False
        )
        
    # === Handoff ===
    def _generate_signature(self, content_bytes: bytes) -> str:
        """使用 SHA-256 HMAC 生成狀態簽章，提供防禦性防篡改校驗"""
        return hmac.new(self.secret_key, content_bytes, hashlib.sha256).hexdigest()
        
    def save_handoff(self, task_state: Dict[str, Any], output_path: Path) -> Path:
        """簽署並保存 Handoff 狀態檔案"""
        output_path = Path(output_path)
        
        # 序列化 State
        state_str = json.dumps(task_state, sort_keys=True)
        sig = self._generate_signature(state_str.encode("utf-8"))
        
        payload = {
            "version": "1.0.0",
            "timestamp": time.time(),
            "signature": sig,
            "state": task_state
        }
        
        # 原子寫入
        temp_path = output_path.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
            
        if output_path.exists():
            output_path.unlink()
        temp_path.rename(output_path)
        
        return output_path
        
    def load_handoff(self, path: Path) -> Optional[Dict[str, Any]]:
        """載入並進行簽章驗證的 Handoff 狀態還原"""
        path = Path(path)
        if not path.exists():
            return None
            
        try:
            with open(path, "r", encoding="utf-8") as f:
                payload = json.load(f)
                
            if "signature" not in payload or "state" not in payload:
                return None
                
            # 驗證 HMAC 簽章
            state_str = json.dumps(payload["state"], sort_keys=True)
            expected_sig = self._generate_signature(state_str.encode("utf-8"))
            
            if not hmac.compare_digest(payload["signature"], expected_sig):
                # 簽章不符，可能被惡意篡改，拒絕載入
                return None
                
            return payload["state"]
        except Exception:
            return None
            
    def get_pause_message(self, level: str) -> str:
        """取得對話中斷通知提示"""
        usage = self.get_usage()
        if level == "warn":
            return (
                f"\n> [!WARNING]\n"
                f"> **[CONTEXT_WARN]** 目前 Token 使用率達 {usage['ratio']:.1%} "
                f"({usage['tokens']:,} / {usage['limit']:,})。\n"
                f"> 請盡快在當前步驟結束後進行收尾，並產出手動 checkpoint 退出。"
            )
        elif level == "critical":
            return (
                f"\n> [!CAUTION]\n"
                f"> **[CONTEXT_CRITICAL]** Token 使用率已高達 {usage['ratio']:.1%} "
                f"({usage['tokens']:,} / {usage['limit']:,})，已達強制暫停閥值！\n"
                f"> 系統已自動將當前進度狀態寫入 `handoff.json`，並強制熔斷退場。"
            )
        return ""

import os
import json
import time
import hashlib
import logging
from typing import Any, Dict

logger = logging.getLogger("RVA_Audit")

class RVAAuditLogger:
    """
    RVA Audit System
    以 Append-only 方式記錄所有 GUI 操作與視覺決策，確保不可否認性 (Non-repudiation)。
    """
    
    def __init__(self, log_dir: str = "data/rva_history"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.current_session_file = os.path.join(
            self.log_dir, 
            f"audit_{time.strftime('%Y%m%d_%H%M%S')}.jsonl"
        )

    def log_action(self, action_type: str, details: Dict[str, Any], screenshot_path: str = None):
        """記錄單一操作"""
        record = {
            "timestamp": time.time(),
            "iso_time": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "action_type": action_type,
            "details": details,
            "screenshot_hash": self._calculate_hash(screenshot_path) if screenshot_path else None
        }

        try:
            with open(self.current_session_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
            logger.debug(f"RVA Audit: Recorded {action_type}")
        except Exception as e:
            logger.error(f"RVA Audit Fail: {e}")

    def _calculate_hash(self, file_path: str) -> str:
        """計算檔案的 SHA256 雜湊"""
        if not os.path.exists(file_path):
            return ""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def create_snapshot(self, description: str):
        """建立當前階段的快照包 (Repudiation protection)"""
        # 未來可整合截圖 + 系統日誌打包成 zip
        pass

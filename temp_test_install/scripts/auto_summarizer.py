import os
import sys
import logging
# pyrefly: ignore [missing-import]
import tiktoken

# 設定日誌
logging.basicConfig(level=logging.INFO, format='[Memory-Sentinel] %(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Tokenizer 配置
TOKENIZER = tiktoken.get_encoding("cl100k_base")

class MemorySentinel:
    def __init__(self, target_file="current.md", threshold=50000):
        self.target_file = target_file
        self.threshold = threshold

    def count_tokens(self, text: str) -> int:
        return len(TOKENIZER.encode(text))

    def check(self):
        """檢查 L1 狀態並發出信號"""
        if not os.path.exists(self.target_file):
            logger.info(f"ℹ️ 檔案不存在: {self.target_file}，跳過檢查。")
            return 0

        with open(self.target_file, "r", encoding="utf-8") as f:
            content = f.read()

        token_count = self.count_tokens(content)
        logger.info(f"📊 目前 {self.target_file} Token 數: {token_count} (閾值: {self.threshold})")

        if token_count > self.threshold:
            logger.warning(f"⚠️ 記憶體超標！請委派 Antigravity 進行智慧摘要 (Delegated Summary Mode)。")
            # 返回特定 Exit Code 2 代表 Overloaded
            return 2
        
        return 0

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="current.md")
    parser.add_argument("--threshold", type=int, default=50000)
    args = parser.parse_args()
    
    sentinel = MemorySentinel(args.file, args.threshold)
    exit_code = sentinel.check()
    sys.exit(exit_code)

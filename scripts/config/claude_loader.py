import os
from pathlib import Path

class ClaudeLoader:
    """
    載入 CLAUDE.md 作為專案規範注入
    """
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.claude_file = self.project_root / "CLAUDE.md"

    def load_prompt_fragment(self) -> str:
        """讀取 CLAUDE.md 並格式化為 Prompt 片段"""
        if not self.claude_file.exists():
            return ""
            
        try:
            with open(self.claude_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                
            if not content:
                return ""
                
            return f"\n--- PROJECT RULES (from CLAUDE.md) ---\n{content}\n--- END RULES ---\n"
        except Exception as e:
            print(f"[ClaudeLoader] Failed to load CLAUDE.md: {e}")
            return ""

    def exists(self) -> bool:
        return self.claude_file.exists()

import json
import uuid
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class MemoryStore:
    """
    分層記憶系統 (L1, L2, L3)
    """
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.state_dir = self.project_root / ".agent-state" / "memory"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self.l1_path = self.state_dir / "session_memory.json"
        self.l2_path = self.state_dir / "project_memory.json"
        
        global_dir = Path.home() / ".autoagent"
        global_dir.mkdir(parents=True, exist_ok=True)
        self.l3_path = global_dir / "global_memory.json"

    def _get_path(self, level: str) -> Path:
        level = level.upper()
        if level == "L1": return self.l1_path
        elif level == "L3": return self.l3_path
        return self.l2_path

    def _load(self, level: str) -> List[Dict]:
        path = self._get_path(level)
        if not path.exists():
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def _save(self, level: str, data: List[Dict]):
        path = self._get_path(level)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def add_memory(self, content: str, level: str = "L2", tags: List[str] = None) -> str:
        data = self._load(level)
        mem_id = str(uuid.uuid4())[:8]
        entry = {
            "id": mem_id,
            "timestamp": datetime.now().isoformat(),
            "content": content,
            "tags": tags or [],
            "focus": False
        }
        data.append(entry)
        self._save(level, data)
        return mem_id

    def list_memories(self, level: str = "L2") -> List[Dict]:
        return self._load(level)

    def delete_memory(self, mem_id: str, level: str = "L2") -> bool:
        data = self._load(level)
        new_data = [m for m in data if not m["id"].startswith(mem_id)]
        if len(new_data) == len(data):
            return False
        self._save(level, new_data)
        return True

    def set_focus(self, mem_id: Optional[str], level: str = "L2") -> bool:
        """
        將指定 mem_id 設為 focus，若 mem_id 為 'clear' 或 None，則解除所有 focus
        """
        data = self._load(level)
        found = False
        for item in data:
            if mem_id and mem_id.lower() != 'clear' and item["id"].startswith(mem_id):
                item["focus"] = True
                found = True
            else:
                item["focus"] = False
                
        self._save(level, data)
        return found if (mem_id and mem_id.lower() != 'clear') else True

    def export_context(self, level: str = "L2") -> str:
        """
        匯出上下文。如果該 level 有任何 focus=True 的記憶，則只顯示那幾條，忽略其他 (專注模式)。
        """
        data = self._load(level)
        focused = [m for m in data if m.get("focus")]
        
        target_list = focused if focused else data
        
        if not target_list:
            return f"[{level}] No context available."
            
        lines = [f"=== Memory Context Export ({level}) ==="]
        for i, m in enumerate(target_list, 1):
            tags = ",".join(m.get("tags", []))
            lines.append(f"\n[{i}] ID: {m['id']} | Tags: {tags}")
            lines.append(f"Content: {m['content']}")
            
        return "\n".join(lines)

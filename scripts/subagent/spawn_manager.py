import asyncio
import json
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path
import os

# 修改問題加版本version: v1.9.0
# Phase 1: SubagentSpawnManager

class SubagentSpawnManager:
    """
    負責建立、監控、回收獨立的背景 AI 子代理任務。
    目前採用 Asyncio 協程模擬輕量級子代理，
    未來可擴充為獨立 Python 子進程以保證環境隔離。
    """
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.state_dir = self.project_root / ".agent-state" / "subagents"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.active_subagents: Dict[str, Dict] = {}

    async def spawn(self, task_spec: Dict[str, Any]) -> str:
        """
        建立一個新的子代理並開始執行任務
        task_spec: { role, prompt, context_files, timeout, budget_tokens }
        返回: subagent_id
        """
        subagent_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        # 初始化子代理狀態
        subagent_info = {
            "id": subagent_id,
            "role": task_spec.get("role", "researcher"),
            "status": "pending",
            "start_time": timestamp,
            "task": task_spec.get("prompt", ""),
            "progress": 0,
            "logs": []
        }
        
        self.active_subagents[subagent_id] = subagent_info
        self._save_state(subagent_id, subagent_info)
        
        # 異步啟動執行
        # [debug printf]
        print(f"[SPAWN] Subagent {subagent_id} spawned for role '{subagent_info['role']}'")
        
        asyncio.create_task(self._run_task(subagent_id, task_spec))
        
        return subagent_id

    async def _run_task(self, subagent_id: str, task_spec: Dict[str, Any]):
        """
        模擬子代理執行邏輯。實際應呼叫 Claude API。
        """
        info = self.active_subagents[subagent_id]
        info["status"] = "running"
        info["logs"].append(f"Task started at {datetime.now().isoformat()}")
        self._save_state(subagent_id, info)

        try:
            # 這裡模擬 API 執行與進度
            timeout = task_spec.get("timeout", 300)
            
            # TODO: 整合 anthropic SDK 呼叫
            # 目前僅先實作進度模擬以驗證前端 Dashboard 整合
            for i in range(1, 101, 20):
                await asyncio.sleep(2) # 模擬工作
                info["progress"] = i
                info["logs"].append(f"Work in progress: {i}%")
                self._save_state(subagent_id, info)
            
            info["status"] = "done"
            info["progress"] = 100
            info["end_time"] = datetime.now().isoformat()
            info["result"] = f"Result of {info['role']} task: Completed successfully."
            
        except Exception as e:
            info["status"] = "fail"
            info["error"] = str(e)
            print(f"[FAIL] Subagent {subagent_id} failed: {e}")
        
        self._save_state(subagent_id, info)
        print(f"[SPAWN] Subagent {subagent_id} finished with status: {info['status']}")

    def _save_state(self, subagent_id: str, data: Dict):
        state_path = self.state_dir / f"{subagent_id}.json"
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        # 同時觸發 Dashboard 狀態更新 (Optionally via status_updater)
        # TODO: 集成自定義狀態面板

    async def collect(self, subagent_id: str) -> Dict:
        """等待子代理完成並回收結果"""
        while subagent_id in self.active_subagents:
            info = self.active_subagents[subagent_id]
            if info["status"] in ["done", "fail"]:
                return info
            await asyncio.sleep(1)
        return {"error": "Subagent not found"}

    async def parallel(self, task_specs: List[Dict]) -> List[Dict]:
        """批次併行執行多個子代理任務"""
        ids = []
        for spec in task_specs:
            sub_id = await self.spawn(spec)
            ids.append(sub_id)
            
        return await asyncio.gather(*[self.collect(sid) for sid in ids])

# 主要功能測試入口
if __name__ == "__main__":
    async def test():
        manager = SubagentSpawnManager(".")
        print("Testing parallel spawn...")
        tasks = [
            {"role": "researcher", "prompt": "Researching Auth flow"},
            {"role": "implementer", "prompt": "Implementing login.py"},
            {"role": "verifier", "prompt": "Running security checks"}
        ]
        results = await manager.parallel(tasks)
        print(f"Parallel Results: {len(results)} tasks closed.")

    asyncio.run(test())

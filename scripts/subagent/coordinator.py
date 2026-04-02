import asyncio
import json
from typing import Any, Dict, List, Optional
from pathlib import Path

# 修改問題加版本version: v1.9.0
# Phase 1: Coordinator

class Coordinator:
    """
    任務調度器：負責接收高階指令 (Goal)，
    分析其子任務並委派給 SubagentSpawnManager 併行執行。
    """
    def __init__(self, manager: Any):
        self.manager = manager # 傳入 SubagentSpawnManager 執行器
        self.active_groups: Dict[str, List] = {}

    async def orchestrate(self, goal: str) -> Dict:
        """
        核心調度入口：
        1. 研究現狀
        2. 生成任務清單
        3. 委派給子代理
        4. 回收結果並彙整報告
        """
        print(f"[COORDINATOR] Orchestrating Goal: {goal}")
        
        # 步驟 A: 通過 LLM 拆解具體子任務 (此處先模擬實作)
        # 實際情況下應進行一系列 Prompting 或 遞歸拆解
        task_specs = self._decompose_goal(goal)
        
        # 步驟 B: 並行執行所有子任務
        print(f"[COORDINATOR] Decomposed into {len(task_specs)} tasks.")
        subagent_results = await self.manager.parallel(task_specs)
        
        # 步驟 C: 整合所有結果生成報告 (Aggregate Report)
        report = self._aggregate_results(goal, subagent_results)
        
        return report

    def _decompose_goal(self, goal: str) -> List[Dict]:
        """
        模擬通過 LLM 生成任務 Spec 清單邏輯。
        """
        # [debug printf]
        print(f"[COORDINATOR] Decomposing goal...")
        
        if "login" in goal.lower() or "auth" in goal.lower():
            return [
                {"role": "researcher", "prompt": f"Analyze existing auth logic for {goal}"},
                {"role": "implementer", "prompt": f"Code the core auth bridge for {goal}"},
                {"role": "verifier", "prompt": f"Audit the auth safety for {goal}"}
            ]
        
        # 默認拆解方案
        return [
            {"role": "planner", "prompt": f"Breakdown implementation steps for {goal}"},
            {"role": "implementer", "prompt": f"Write initial draft for {goal}"}
        ]

    def _aggregate_results(self, goal: str, results: List[Dict]) -> Dict:
        """
        結果彙整邏輯。
        """
        print(f"[COORDINATOR] Aggregating results for '{goal}'")
        summary = {
            "goal": goal,
            "status": "success" if all(r.get("status") == "done" for r in results) else "partial",
            "findings": [r.get("result", "") for r in results if r.get("status") == "done"],
            "failures": [r.get("id") for r in results if r.get("status") != "done"]
        }
        return summary

# 測試入口
if __name__ == "__main__":
    from scripts.subagent.spawn_manager import SubagentSpawnManager
    
    async def test():
        mgr = SubagentSpawnManager(".")
        cd = Coordinator(mgr)
        final_report = await cd.orchestrate("Implement secure login flow")
        print(f"Final Coordinator Report: {json.dumps(final_report, indent=2)}")

    asyncio.run(test())

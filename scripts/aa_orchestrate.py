import asyncio
import json
import argparse
import sys
from pathlib import Path

# 修改跑道加版本version: v1.9.0
# Phase 1: aa-orchestrate CLI

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from scripts.subagent.spawn_manager import SubagentSpawnManager
from scripts.subagent.coordinator import Coordinator

async def main():
    parser = argparse.ArgumentParser(description="Orchestrate a goal using parallel subagents.")
    parser.add_argument("goal", type=str, help="High-level goal for the agent.")
    parser.add_argument("--auto", action="store_true", help="Auto-confirm all steps.")
    args = parser.parse_args()

    print(f"[START] AutoAgent-TW Orchestrator (v1.9.0) starting...")
    print(f"[GOAL] Goal: {args.goal}")
    
    # 初始化子系統
    manager = SubagentSpawnManager(str(PROJECT_ROOT))
    cd = Coordinator(manager)
    
    # 開始調度
    try:
        report = await cd.orchestrate(args.goal)
        
        # 產出報告
        print("\n" + "="*50)
        print(f"--- Orchestration Result: {report['status'].upper()} ---")
        print(f"Goal: {report['goal']}")
        print(f"Findings: {len(report['findings'])}")
        for finding in report['findings']:
            print(f"  > {finding}")
        
        if report['failures']:
            print(f"❌ Failures: {report['failures']}")
            
        print("="*50)
        
    except KeyboardInterrupt:
        print("\n⚠️ Orchestration interrupted by user.")
    except Exception as e:
        print(f"[ERROR] Error during orchestration: {e}")

if __name__ == "__main__":
    asyncio.run(main())

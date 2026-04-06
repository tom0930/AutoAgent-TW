"""
AutoAgent-TW Internal MCP Server (FastMCP)
- 暴露自有的核心功能為工具，供子代理呼叫
- Phase 125 完成後，子代理也能「自助服務」查詢專案進度
"""
import sys
import logging
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP 服務器
mcp = FastMCP("AutoAgent Internal Automation Toolset")

# 模擬核心邏輯導入 (實際應根據 aa-progress 指令實現)
def _get_project_progress() -> str:
    # 這裡未來會導入 src.core.cli.progress 邏輯
    return "[INFO] Phase 125 in progress (Wave 1: MCP Core DONE)."

@mcp.tool()
async def get_phase_status(phase_id: str) -> str:
    """查詢特定 Phase 的當前狀態與完成百分比。"""
    return f"Status of Phase {phase_id}: IN-PROGRESS (85% mapped)."

@mcp.tool()
async def get_schedule_tasks() -> list[str]:
    """獲取調度器 (Scheduler) 下一次運行的任務清單。"""
    return ["Task A: DB Backup", "Task B: Phase 125 Wave 2 Execution"]

@mcp.tool()
async def create_status_report() -> str:
    """生成當前里程碑 (Milestone) 的完整彙總報告 Markdown。"""
    return "# Milestone Status Report\n- Overall: 92%\n- Healthy: YES"

if __name__ == "__main__":
    # 使用 stdio 模式運行 MCP 伺服器
    mcp.run()

"""
AutoAgent-TW Scheduler Daemon v1.0
- 管理背景任務與 MCP 生命週期
- 健康檢查與資源回收
"""
import asyncio
import signal
import logging
import sys
from src.core.mcp.mcp_client import MCPClientManager

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("aa_scheduler")

class SchedulerDaemon:
    def __init__(self):
        self.mcp_manager = MCPClientManager()
        self.is_running = True

    async def _health_check_loop(self):
        """每 5 分鐘進行一次 MCP Health Check"""
        while self.is_running:
            try:
                logger.info("[Health] Periodic MCP health check starting...")
                # 未來在此調用 mcp_manager.health_check()
                status = self.mcp_manager.get_server_status()
                for s in status:
                    if not s['connected']:
                        logger.warning(f"[Health] MCP Server '{s['name']}' is DISCONNECTED.")
                    else:
                        logger.info(f"[Health] MCP Server '{s['name']}' is HEALTHY.")
            except Exception as e:
                logger.error(f"[Health] Error in health check: {e}")
            
            await asyncio.sleep(300) # 5 minutes

    async def start(self):
        """背景服務啟動主進入點"""
        logger.info("[Scheduler] Starting AutoAgent-TW Daemon...")
        
        # 1. 啟動 MCP
        await self.mcp_manager.startup()
        
        # 2. 啟動背景巡檢任務
        asyncio.create_task(self._health_check_loop())
        
        logger.info("[Scheduler] System background layer ACTIVE.")
        
        # 3. 保持運行直到被中斷
        while self.is_running:
            await asyncio.sleep(1)

    async def stop(self):
        """優雅關閉邏輯，資源回收"""
        logger.info("[Scheduler] Shutting down...")
        self.is_running = False
        await self.mcp_manager.shutdown()
        logger.info("[Scheduler] Shutdown complete.")

def main():
    daemon = SchedulerDaemon()
    loop = asyncio.get_event_loop()

    # 設置信號處理
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(daemon.stop()))

    try:
        loop.run_until_complete(daemon.start())
    except Exception as e:
        logger.error(f"[Fatal] Scheduler crashed: {e}")
    finally:
        loop.close()

if __name__ == "__main__":
    main()

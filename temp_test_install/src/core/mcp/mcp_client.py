"""
AutoAgent-TW MCP Client Manager v2
- asyncio.gather 並行啟動所有 server（避免單一 server 阻塞）
- Exponential backoff retry（3 次，30s timeout）
- get_server_status() 暴露給 Dashboard 與 Scheduler
"""
import asyncio
import json
import logging
import os
import re
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Any, List, Dict, Optional
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool
# pyrefly: ignore [missing-import]
from src.core.mcp.registry import MCPToolRegistry

logger = logging.getLogger("aa_mcp")

MAX_RETRIES: int = 3
CONNECT_TIMEOUT: float = 30.0


@dataclass
class ServerStatus:
    """連接狀態快照，供介面與調度器查詢"""
    name: str
    connected: bool
    tool_count: int = 0
    error: Optional[str] = None
    last_health_check: float = 0.0


class MCPClientManager:
    """
    負責伺服器生命週期的核心管理器。
    - 啟動並行连接 (Startup)
    - 任務健康檢查 (Health Check)
    - 子代理工具發現 (Tool Gathering)
    - 系統優雅關閉 (Shutdown/Cleanup)
    """

    def __init__(self, config_path: str = ".agents/mcp_servers.json"):
        self.config_path = Path(config_path)
        self.registry: MCPToolRegistry = MCPToolRegistry()
        self._client: Optional[MultiServerMCPClient] = None
        self._status: Dict[str, ServerStatus] = {}
        # 暫存 client 物件便於 lifecycle 管理
        self._raw_clients: List[Any] = []

    def _load_config(self) -> dict:
        """讀取 mcp_servers.json，並替換 ${VAR} 環境變數，落實安全策略。"""
        if not self.config_path.exists():
            logger.warning(f"MCP configuration not found at {self.config_path}")
            return {"servers": []}

        raw = self.config_path.read_text(encoding="utf-8")

        def replace_env(m: re.Match) -> str:
            val = os.environ.get(m.group(1), "")
            if not val:
                logger.warning(f"[MCP] Env var '{m.group(1)}' not set!")
                # 回傳空字串或原變數占位符，視策略而定
            return val

        # 替換 ${SECRET_NAME} 為真實環境變數
        hydrated = re.sub(r"\$\{([^}]+)\}", replace_env, raw)
        return json.loads(hydrated)

    async def startup(self) -> None:
        """並行啟動所有已啟用的伺服器，落實快速啟動策略。"""
        config = self._load_config()
        enabled_servers = [s for s in config.get("servers", []) if s.get("enabled", True)]

        if not enabled_servers:
            logger.info("[MCP] No servers are enabled for connection.")
            return

        # 並行連接所有 server
        results = await asyncio.gather(
            *[self._connect_server_with_retry(s) for s in enabled_servers],
            return_exceptions=True
        )

        for server, result in zip(enabled_servers, results):
            if isinstance(result, Exception):
                logger.error(f"[MCP] Critical failure connecting to '{server['name']}': {result}")

    async def _connect_server_with_retry(self, server_cfg: dict) -> None:
        """依回退機制嘗試連接單一 MCP 伺服器。"""
        name = server_cfg["name"]
        last_error = "Unknown error"
        for attempt in range(MAX_RETRIES):
            try:
                # 實務上在此呼叫 langchain_mcp_adapters 的初始化邏輯
                # 假設 MultiServerMCPClient 已對各種 transport (stdio/sse) 封裝
                tools = await asyncio.wait_for(
                    self._do_connect_logic(server_cfg),
                    timeout=CONNECT_TIMEOUT
                )
                self.registry.register(name, tools)
                self._status[name] = ServerStatus(
                    name=name,
                    connected=True,
                    tool_count=len(tools)
                )
                logger.info(f"[MCP] '{name}' connected. Registered {len(tools)} tools.")
                return
            except Exception as e:
                last_error = str(e)
                wait = 2 ** attempt
                logger.warning(f"[MCP] Failed to connect '{name}' (Attempt {attempt+1}/{MAX_RETRIES}): {e}. Retrying in {wait}s...")
                await asyncio.sleep(wait)
        
        # 最終失敗紀錄
        self._status[name] = ServerStatus(name=name, connected=False, error=last_error)

    async def _do_connect_logic(self, cfg: dict) -> List[BaseTool]:
        """封裝後的連接邏輯，核心與 stdio/HTTP 等相關。"""
        from langchain_mcp_adapters.tools import load_mcp_tools
        
        # 根據 cfg 構造連接參數
        # 實測確認：需使用 load_mcp_tools(None, connection=config_dict) 模式
        # 且 config_dict 必須包含 'transport' 字串鍵
        try:
            if cfg.get("transport") == "stdio":
                # 直接構造配置字典
                mcp_config = {
                    "command": sys.executable if cfg.get("command") == "python" else cfg.get("command"),
                    "args": cfg.get("args", []),
                    "env": cfg.get("env"),
                    "transport": "stdio"
                }
                
                # 載入工具 (需使用 await，回傳的是 coroutine)
                tools = await load_mcp_tools(
                    None,
                    # pyrefly: ignore [bad-argument-type]
                    connection=mcp_config,
                    server_name=cfg.get("name")
                )
                
                return list(tools)
        except Exception:
             logger.error(f"[MCP] Error in _do_connect_logic for '{cfg.get('name')}'")
             raise 
        
        return []

    async def shutdown(self) -> None:
        """優雅清理資源。"""
        logger.info("[MCP] Gracefully shutting down all connections.")
        for stack in self._raw_clients:
            try:
                await stack.aclose()
            except Exception as e:
                logger.error(f"[MCP] Error closing connection stack: {e}")
        self._raw_clients.clear()

    def get_tools_for_agent(
        self,
        server_names: Optional[List[str]] = None,
        capability_filter: Optional[str] = None
    ) -> List[BaseTool]:
        """取得供代理使用的工具集合。"""
        if server_names:
            tools = self.registry.get_server_tools(server_names)
        else:
            tools = self.registry.get_all_tools()

        if capability_filter:
            tools = [t for t in tools if capability_filter in t.name]

        return tools

    def get_server_status(self) -> List[dict]:
        """返回儀表板展示用的狀態列表。"""
        return [
            {
                "name": s.name,
                "connected": s.connected,
                "tool_count": s.tool_count,
                "error": s.error
            }
            for s in self._status.values()
        ]

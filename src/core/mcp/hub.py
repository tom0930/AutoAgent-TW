"""
AI Harness MCP Hub
功能：MCP (Model Context Protocol) 伺服器發現、路由、代理
版本：v1.0.0
"""
import json
import asyncio
import os
import subprocess
import threading
import time
import uuid
import hashlib
import secrets
import struct
import base64
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Set
from enum import Enum
from abc import ABC, abstractmethod
import logging


class MCPTransport(Enum):
    STDIO = "stdio"
    HTTP = "http"
    WEBSOCKET = "websocket"


@dataclass
class MCPTool:
    """MCP Tool 定義"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    server_id: str
    server_name: str


@dataclass
class MCPToolCall:
    """MCP Tool 呼叫請求"""
    tool_name: str
    arguments: Dict[str, Any]
    call_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.call_id:
            self.call_id = f"call_{uuid.uuid4().hex[:12]}"  # type: ignore[assignment]


@dataclass
class MCPToolResult:
    """MCP Tool 呼叫結果"""
    call_id: str | None
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0


class MCPTransportBase(ABC):
    """MCP 傳輸層抽象基類"""
    
    @abstractmethod
    async def start(self):
        """啟動傳輸"""
        pass
    
    @abstractmethod
    async def stop(self):
        """停止傳輸"""
        pass
    
    @abstractmethod
    async def send(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """發送訊息"""
        pass
    
    @abstractmethod
    async def receive(self) -> Optional[Dict[str, Any]]:
        """接收訊息"""
        pass


class StdioTransport(MCPTransportBase):
    """STDIO 傳輸層 - 用於本地 MCP 伺服器"""
    
    def __init__(self, command: str, args: List[str], env: Optional[Dict[str, str]] = None):
        self.command = command
        self.args = args
        self.env = env or {}
        self.process: Optional[subprocess.Popen] = None
        self._lock = threading.Lock()
    
    async def start(self):
        """啟動 STDIO 伺服器"""
        full_env = {**os.environ, **self.env}
        
        self.process = subprocess.Popen(
            [self.command] + self.args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=full_env,
            text=False  # 使用二進制模式
        )
    
    async def stop(self):
        """停止 STDIO 伺服器"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
    
    async def send(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """發送 JSON-RPC 訊息"""
        with self._lock:
            if not self.process:
                raise RuntimeError("Transport not started")
            
            # 序列化為 JSON lines
            content = json.dumps(message, ensure_ascii=False)
            content_bytes = (content + '\n').encode('utf-8')
            
            self.process.stdin.write(content_bytes)  # type: ignore[union-attr]
            self.process.stdin.flush()  # type: ignore[union-attr]
            
            # 讀取回應
            line = self.process.stdout.readline()  # type: ignore[union-attr]
            if not line:
                raise RuntimeError("No response from MCP server")
            
            return json.loads(line.decode('utf-8'))
    
    async def receive(self) -> Optional[Dict[str, Any]]:
        """接收訊息（非同步讀取）"""
        import select
        
        if not self.process:
            return None
        
        # 使用 select 檢查是否有資料可讀
        if select.select([self.process.stdout], [], [], 0.1)[0]:
            line = self.process.stdout.readline()  # type: ignore[union-attr]
            if line:
                return json.loads(line.decode('utf-8'))
        
        return None


class MCPHub:
    """
    MCP Hub - 多伺服器路由中心
    
    功能：
    - MCP 伺服器發現與管理
    - Tool 路由
    - 請求/回應轉換
    - 連接池管理
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, config_path: Optional[Path] = None, config: Optional[Dict] = None):
        self.config_path = config_path
        self.config = config or {}
        self.logger = logging.getLogger("harness.mcp")
        
        # 伺服器註冊表
        self.servers: Dict[str, Dict[str, Any]] = {}
        
        # Tool 註冊表
        self.tools: Dict[str, MCPTool] = {}
        
        # 傳輸層
        self.transports: Dict[str, MCPTransportBase] = {}
        
        # 安全白名單
        self.tool_whitelist: Set[str] = set(self.config.get('tool_whitelist', []))
        self.allowed_servers: Set[str] = set(self.config.get('allowed_servers', []))
        
        # Rate limiting
        self.rate_limits: Dict[str, Dict[str, Any]] = {}  # server -> tool -> {count, window_start}
        self.rate_limit_window = 60  # 60 秒窗口
        self.rate_limit_max = 100  # 每窗口最多 100 次
        
        # 載入配置
        self._load_config()
    
    def _load_config(self):
        """載入 MCP 配置"""
        if not self.config_path:
            return
        
        if not self.config_path.exists():
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            servers = config.get('servers', {})
            for server_id, server_config in servers.items():
                self.register_server(server_id, server_config)
                
        except Exception as e:
            self.logger.error(f"Failed to load MCP config: {e}")
    
    def register_server(self, server_id: str, config: Dict[str, Any]):
        """
        註冊 MCP 伺服器
        
        Args:
            server_id: 伺服器 ID
            config: 伺服器配置
                - type: stdio | http | websocket
                - command: 執行命令（stdio）
                - args: 命令參數
                - env: 環境變數
                - url: 伺服器 URL（http/websocket）
                - enabled: 是否啟用
        """
        if self.allowed_servers and server_id not in self.allowed_servers:
            self.logger.warning(f"Server {server_id} not in allowed list")
            return
        
        server = {
            'id': server_id,
            'name': config.get('name', server_id),
            'type': MCPTransport(config.get('type', 'stdio')),
            'command': config.get('command', ''),
            'args': config.get('args', []),
            'env': config.get('env', {}),
            'url': config.get('url', ''),
            'enabled': config.get('enabled', True),
            'tools': [],
            'started_at': 0
        }
        
        self.servers[server_id] = server
        self.logger.info(f"Registered MCP server: {server_id} ({server['type'].value})")
    
    async def start_server(self, server_id: str):
        """啟動 MCP 伺服器"""
        server = self.servers.get(server_id)
        if not server:
            raise ValueError(f"Server not found: {server_id}")
        
        if server['type'] == MCPTransport.STDIO:
            transport = StdioTransport(
                server['command'],
                server['args'],
                server['env']
            )
            await transport.start()
            self.transports[server_id] = transport
            server['started_at'] = time.time()
            
            # 探索 Tool
            await self._discover_tools(server_id)
    
    async def _discover_tools(self, server_id: str):
        """探索伺服器提供的 Tools"""
        transport = self.transports.get(server_id)
        if not transport:
            return
        
        # 發送工具列表請求
        request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/list",
            "params": {}
        }
        
        try:
            response = await transport.send(request)
            
            if 'result' in response and 'tools' in response['result']:
                tools = response['result']['tools']
                for tool_def in tools:
                    tool = MCPTool(
                        name=tool_def['name'],
                        description=tool_def.get('description', ''),
                        input_schema=tool_def.get('inputSchema', {}),
                        server_id=server_id,
                        server_name=self.servers[server_id]['name']
                    )
                    self.tools[tool.name] = tool
                    self.servers[server_id]['tools'].append(tool.name)
                    
        except Exception as e:
            self.logger.error(f"Tool discovery failed for {server_id}: {e}")
    
    async def stop_server(self, server_id: str):
        """停止 MCP 伺服器"""
        transport = self.transports.get(server_id)
        if transport:
            await transport.stop()
            del self.transports[server_id]
        
        # 移除該伺服器的 Tools
        to_remove = [name for name, tool in self.tools.items() 
                     if tool.server_id == server_id]
        for name in to_remove:
            del self.tools[name]
    
    def list_servers(self, enabled_only: bool = True) -> List[Dict[str, Any]]:
        """列出所有 MCP 伺服器"""
        result = []
        
        for server in self.servers.values():
            if enabled_only and not server['enabled']:
                continue
            
            result.append({
                'id': server['id'],
                'name': server['name'],
                'type': server['type'].value,
                'tool_count': len(server['tools']),
                'running': server['id'] in self.transports,
                'started_at': server['started_at']
            })
        
        return result
    
    def list_tools(self, 
                   server_id: Optional[str] = None,
                   include_internal: bool = False) -> List[Dict[str, Any]]:
        """列出所有可用 Tools"""
        result = []
        
        for tool in self.tools.values():
            if server_id and tool.server_id != server_id:
                continue
            
            result.append({
                'name': tool.name,
                'description': tool.description,
                'server_id': tool.server_id,
                'server_name': tool.server_name,
                'input_schema': tool.input_schema
            })
        
        return result
    
    async def call_tool(self, call: MCPToolCall) -> MCPToolResult:
        """
        呼叫 MCP Tool
        
        Args:
            call: Tool 呼叫請求
        
        Returns:
            MCPToolResult 執行結果
        """
        start_time = time.time()
        
        tool = self.tools.get(call.tool_name)
        if not tool:
            return MCPToolResult(
                call_id=call.call_id,
                success=False,
                error=f"Tool not found: {call.tool_name}"
            )
        
        # 安全檢查
        if self.tool_whitelist and call.tool_name not in self.tool_whitelist:
            return MCPToolResult(
                call_id=call.call_id,
                success=False,
                error=f"Tool not in whitelist: {call.tool_name}"
            )
        
        # Rate limiting
        if not self._check_rate_limit(tool.server_id, call.tool_name):
            return MCPToolResult(
                call_id=call.call_id,
                success=False,
                error="Rate limit exceeded"
            )
        
        # 確保伺服器運行
        if tool.server_id not in self.transports:
            try:
                await self.start_server(tool.server_id)
            except Exception as e:
                return MCPToolResult(
                    call_id=call.call_id,
                    success=False,
                    error=f"Failed to start server: {e}",
                    execution_time_ms=(time.time() - start_time) * 1000
                )
        
        # 發送 Tool Call 請求
        transport = self.transports[tool.server_id]
        request = {
            "jsonrpc": "2.0",
            "id": call.call_id,
            "method": "tools/call",
            "params": {
                "name": call.tool_name,
                "arguments": call.arguments
            }
        }
        
        try:
            response = await transport.send(request)
            
            execution_time = (time.time() - start_time) * 1000
            
            if 'error' in response:
                return MCPToolResult(
                    call_id=call.call_id,
                    success=False,
                    error=response['error'].get('message', 'Unknown error'),
                    execution_time_ms=execution_time
                )
            
            return MCPToolResult(
                call_id=call.call_id,
                success=True,
                result=response.get('result', {}),
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            return MCPToolResult(
                call_id=call.call_id,
                success=False,
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000
            )
    
    def _check_rate_limit(self, server_id: str, tool_name: str) -> bool:
        """檢查 Rate Limit"""
        now = time.time()
        
        if server_id not in self.rate_limits:
            self.rate_limits[server_id] = {}
        
        server_limits = self.rate_limits[server_id]
        
        if tool_name not in server_limits:
            server_limits[tool_name] = {'count': 1, 'window_start': now}
            return True
        
        tool_limit = server_limits[tool_name]
        window_start = tool_limit['window_start']
        
        # 檢查是否需要重置窗口
        if now - window_start > self.rate_limit_window:
            tool_limit['count'] = 1
            tool_limit['window_start'] = now
            return True
        
        # 檢查是否超限
        if tool_limit['count'] >= self.rate_limit_max:
            return False
        
        tool_limit['count'] += 1
        return True
    
    async def start_all(self):
        """啟動所有已註冊的 MCP 伺服器"""
        for server_id, server in self.servers.items():
            if server['enabled']:
                try:
                    await self.start_server(server_id)
                except Exception as e:
                    self.logger.error(f"Failed to start {server_id}: {e}")
    
    async def stop_all(self):
        """停止所有 MCP 伺服器"""
        for server_id in list(self.transports.keys()):
            try:
                await self.stop_server(server_id)
            except Exception as e:
                self.logger.error(f"Failed to stop {server_id}: {e}")


def main():
    """測試"""
    import tempfile
    import os
    
    hub = MCPHub()
    
    # 測試註冊伺服器
    hub.register_server("test", {
        "type": "stdio",
        "command": "echo",
        "args": ["test"]
    })
    
    print("=== MCP Servers ===")
    for server in hub.list_servers():
        print(f"  {server['id']}: {server['type']}")
    
    print("\n=== Available Tools ===")
    for tool in hub.list_tools():
        print(f"  {tool['name']}: {tool['description']}")


if __name__ == '__main__':
    main()

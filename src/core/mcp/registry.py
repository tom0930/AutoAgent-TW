"""
MCPToolRegistry v2
- server_name::tool_name 命名空間防衝突
- get_server_tools() 按 server 過濾
- list_summary() 供 /aa-mcp list --verbose 使用（含 schema）
"""
from dataclasses import dataclass, field
from langchain_core.tools import BaseTool


@dataclass
class MCPToolRegistry:
    _tools: dict[str, BaseTool] = field(default_factory=dict)
    _tool_to_server: dict[str, str] = field(default_factory=dict)

    def unregister_server(self, server_name: str) -> None:
        """卸載指定伺服器的所有工具，支援熱重載 (Hot-Swap)"""
        keys_to_remove = [k for k, v in self._tool_to_server.items() if v == server_name]
        for k in keys_to_remove:
            self._tools.pop(k, None)
            self._tool_to_server.pop(k, None)

    def register(self, server_name: str, tools: list[BaseTool]) -> None:
        """將多個工具註冊到指定伺服器的命名空間中"""
        # 第一步：確保單例註冊 (Singleton Enforcement)
        self.unregister_server(server_name)
        
        for tool in tools:
            # 建立具備命名空間的工具名稱
            namespaced_name = f"{server_name}::{tool.name}"
            # 為工具設定一個新的描述性名稱（部分模型可能需要）
            self._tools[namespaced_name] = tool
            self._tool_to_server[namespaced_name] = server_name

    def get_all_tools(self) -> list[BaseTool]:
        """回傳所有已註冊的 MCP 工具"""
        return list(self._tools.values())

    def get_server_tools(self, server_names: list[str]) -> list[BaseTool]:
        """按伺服器名稱列表過濾工具"""
        return [t for k, t in self._tools.items() if self._tool_to_server[k] in server_names]

    def list_summary(self, verbose: bool = False) -> list[dict]:
        """
        供 CLI 工具彙總展示
        verbose=False: [{name, server, description}]
        verbose=True:  + input_schema
        """
        result = []
        for key, tool in self._tools.items():
            entry = {
                "name": key,
                "server": self._tool_to_server[key],
                "description": tool.description,
            }
            if verbose:
                # 取得參數結構
                entry["input_schema"] = getattr(tool, "args_schema", None)
            result.append(entry)
        return result

# 🔍 Research: MCP & Agent Memory Fix (Phase 149)

## 1. 記憶體洩漏點分析 (Leak Points)

### A. MCP Server (Node.js)
- **問題**: `notebooklm-mcp` 與 `context7-mcp` 在大型對話中會累積 JSON 緩衝。
- **觀察**: `tasklist` 顯示多個 `node.exe` 佔用 80MB+。若對話重啟但行程未關閉，會形成殭屍進程。
- **影響**: 若有 10 個孤立進程，將佔用 ~1GB RAM。

### B. mcp-router (Python)
- **問題**: `thought_chain` 列表會隨著對話持續增長。
- **優化建議**: 限制緩衝大小至最近 50 個 steps。

### C. Vision Engine (667MB Bloat)
- **問題**: 影像中間副本傳輸未釋放。

## 2. Windows 進程收割 (Process Reaping)
- 實作 `Agent Reaper` 工具，使用 `psutil` 識別並清理孤立進程。

## 3. 資安考量 (Security)
- 確保 Reaper 不會誤殺核心系統行程（如 `wininit.exe`, `services.exe`）。

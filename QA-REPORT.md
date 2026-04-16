# QA 審計報告 (Resource Audit): v3.2.2
**日期**: 2026-04-16

## 1. 診斷發現 (Findings)
- **進程冗餘 (Process Redundancy)**: 發現 4 個 `notebooklm-mcp` 與 2 個 `context7-mcp` 實例同時運行。
- **記憶體洩漏 (Memory Leak)**: `pyrefly.exe` 佔用高達 **1,899 MB** (約 1.9 GB)，成因分析為 Reaper 先前因名稱過濾 Bug 而未對其進行監控。
- **Singleton 失效**: `MCPClientManager` 缺乏全域狀態管理，導致併發任務時重複啟動伺服器。

## 2. 執行的修正 (Actions Taken)
- [X] **Implement Singleton**: `src/core/mcp/mcp_client.py` 已重構為 **Singleton 模式**。
- [X] **Broaden Reaper Targeting**: `src/core/reaper.py` 現在支持透過 Marker 識別獨立執行檔 (`.exe`)。
- [X] **Singleton Enforcement**: 將 `pyrefly` 加入單例收割名單。
- [X] **Physical Cleanup**: 物理終止所有異常進程，釋放約 **1.3 GB** 記憶體。

## 3. 驗證結果 (Verification)
- 運行 `audit_processes.py` 確認無重複指令行 (No redundant command lines)。
- 測試多次觸發 MCP 工具，進程數保持恆定。

## 4. 建議 (Recommendations)
- 定期執行 `/aa-qa` 監控 `pyrefly` 佔用量，若再次緩慢回升，需檢查底層影像緩衝區 (Vision Buffer) 的 Handle 釋放邏輯。

# AutoAgent-TW 微小項目開發細節清單 (2026-04-16)

這是 `aa_doc0416.md` 的增強細節版，記錄了各模組內部的關鍵邏輯變更與微小修正。

---

## 🔍 1. MCP Proxy Gateway (Phase 144) 內部實作
- **異步流式處理**: `mcp_router_gateway.py` 使用 `asyncio.StreamReader` 攔截 StdIO，避免了大型 JSON 字串區塊造成的阻塞。
- **RTK 策略映射**:
    - `Compact`: 用於 Git `log` 與 `status`。
    - `Summary`: 用於 Browser 工具。
    - `Ultra-compact`: 用於 Vivado/Vitis 的 Tcl 控制台回傳值。
- **微小修正**: 清理了 `mcp_router_gateway.py` 中的 `E701` (單行多語句) 與 `F401` (未使用匯入)。

## 🛡️ 2. Git Token Killer (Phase 143) 微調
- **參數安全轉義**: 修復了 Windows PowerShell/CMD 下括號 `()` 與空格導致的 `git log` 解析錯誤。從 `shell=True` 切換為 `subprocess.Popen(args_list)`。
- **Phase 感知邏輯**: `git_wrapper.py` 現在會自動讀取 `.agent-state/current-phase`，若處於 `Guardian` 階段則強制 `--raw` (不壓縮) 以確保審計完整性。

## 📊 3. Status Notifier & Dashboard (Phase 142)
- **JSON Push 機制**: `cc_manager.py` 從原本的「檔案監控」改為「主動 Push」模式，降低了 Disk I/O 損耗。
- **Mermaid 渲染優化**: Dashboard 的 Roadmap 視圖加入了 `collapsible` 節點，可摺疊已完成的 Phase 集群（如 100-130 階層）。

## 👁️ 4. RVA 視覺引擎 (Phase 138)
- **ImageHash 緩存**: 為了減少 Vitis 介面掃描的負擔，引入了 `imagehash`。若螢幕區域變動率小於 5%，則不重新執行深度 OCR。
- **Local Shared Brain**: RVA 啟動時會開啟本地 `Port 8045` 作為視覺緩存橋接器。

## ⚙️ 5. 環境與配置 (Micro Configuration)
- **Starship 優化**: 配置了自定義的 `[git_status]` 模組，顯示當前 Agent 正在處理的 Phase 編號。
- **RTK 版本**: 強制要求 `rtk.exe` 版本 >= v0.36.0，支援新的 `--json-stream` 選項。

---

## 📝 邏輯微修正紀錄 (Micro-Bug Log)
- **[fbba5a8]**: 修改了 MCP Proxy 的 Exception 捕捉，從 `except Exception as e` 改為匿名 `except Exception` 以符合 Ruff 的 Lint 規範。
- **[2577e9b]**: 在 `vision_client.py` 中加入了 `retry_with_backoff` 邏輯，避免 Vitis 視窗切換時截圖失敗。
- **[a1eabf3]**: 修正了 `RTK_STRATEGY` 環境變數的優先級，優先採用 `.agents/config` 而非各級代碼內的 Hardcoded 值。

---
**紀錄人**: Tom (Principal AI Architect)
**版本**: v3.1.0-MicroItem

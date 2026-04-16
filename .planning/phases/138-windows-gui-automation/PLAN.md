# Phase 138: Windows GUI Automation (RVA Engine with Vision Fallback)

本計畫基於優化後的 `CONTEXT.md`，旨在實作專為硬體韌體自動化設計的工業級 Windows GUI 自動化引擎。

## 🛡️ User Review Required

> [!IMPORTANT]
> 此實作將會建立 **RVA_Vision_Client MCP Server**，它具有真實滑鼠點擊 (Click/Action) 權限。
> 請特別確認：對於具備破壞性的特徵字串（例如 `"Erase"`, `"Program"`, `"Format"`），是否必須**強制**啟用 Phase 153 的 `Human-in-the-loop` 對話框授權？目前架構預設為「未授權即阻擋」。

## 🛠️ Proposed Changes

本階段將集中於建立新的 RVA (Robotic Vision Automation) 基礎架構。

---

### Core Automator Module (src/core/rva)

#### [NEW] `src/core/rva/rva_engine.py`
這是混合模式控制引擎的核心：
- 實作 `pywinauto` (UIA Backend) 的快速控制路徑。
- 負責呼叫 Window RECT 並裁切目標軟體邊界，執行灰階處理並發送給 Vision Client。
- 接收 `[0.0, 1.0]` 的正規化邊界框並轉換為 DPI-Aware 的實際像素座標。

#### [NEW] `src/core/rva/vision_client.py`
與 Antigravity (`aa-bridge`) 介接的用戶端：
- 使用 `anthropic` / `google-genai` SDK 傳送局部螢幕截圖。
- 統一 System Prompt，嚴格要求只回傳 `{"bbox": [ymin, xmin, ymax, xmax]}`。

#### [NEW] `src/core/rva/rva_audit.py`
資安與防護模組：
- 實作防抖動 (ImageHash Caching) 與 900秒 Timeout Watchdog。
- 把每一次 RVA 操作跟截圖寫入 `scratch/rva_audit.log` 確保可追溯性 (Repudiation protection)。
- 實作全域 FailSafe (滑鼠拉到螢幕邊緣即終止進程)。

---

### MCP Interface (src/core/mcp)

#### [NEW] `src/core/mcp/rva_server.py`
封裝 RVA 核心邏輯的 MCP Server：
- 將暴露單一核心工具 `rva_click`，支援 JSON schema (包含 `target`, `action_type`, `require_human_auth`)。
- 在觸發危險動作時，串接 Phase 153 的人類驗證合約系統。

#### [MODIFY] `C:\Users\TOM\.gemini\antigravity\mcp_config.json`
- 更新全域設定檔，將新撰寫的 `rva_server.py` 註冊為 `rva-mcp` 服務，讓它與我們剛在 Phase 146 完成的 `mcp_router_gateway.py` 一起協同運作。

## ❓ Open Questions

> [!WARNING]
> 有關截圖效能：局部截圖會使用 Python 的 `mss` + `Pillow` 來進行。為了避免佔用過多記憶體，預設會將截圖縮放至最長邊 `1024px` 並以 JPEG (品質 70) 儲存送給 LLM，這樣足以應付文字跟特徵辨識嗎？若 Vitis GUI 切得很碎，是否考慮保留較高品質？

## 🧪 Verification Plan

### Automated Tests
- [ ] 撰寫 `test_rva_engine.py`：啟動一個標準的 Windows 小算盤 (Calc.exe)，利用 `rva_click` 工具發送 `{"target": "9", "action_type": "click"}`。
- [ ] 測試 UIA 落後 (Fallback) 情境：故意關閉 `pywinauto` 路徑，強迫系統走 Vision 截圖邏輯點擊 "=".

### Manual Verification
- [ ] 請開發者手動執行測試腳本，觀察滑鼠是否在螢幕角落拉至邊緣時能立刻產生 `FailSafeException`。
- [ ] 對特定的敏感關鍵字觸發 `Human-in-the-loop`，確認是否彈出 CLI 警告要求手動打 `y` 才能按下去。

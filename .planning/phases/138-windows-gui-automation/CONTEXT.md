# Architectural Context: Phase 138 — Windows GUI Automation (RVA & Vision Integration)

## 🎯 任務目標與意圖挖掘 (Context & Intent)
相較於常規的 API 串接或網頁爬蟲，許多遺留的 Windows 原生應用程式（特別是硬體開發與燒錄工具，如 **Xilinx SDK, iMPACT, Vitis GUI**）缺乏開放標準接口。
本階段的目標是建構一套具備「視覺感知 (Vision)」與「動態操作 (RVA - Robotic Vision Automation)」的自動化驅動引擎。
特別是為了適配 `uart2mcp` 測試框架，這套 RVA 引擎將允許 Agent 透過電腦視覺去操控這些封閉的硬體 IDE，進而達成韌體自動化編譯、燒錄與硬體在環 (Hardware-In-the-Loop) 的全閉環控制。

## 🛠️ 架構選型與 Trade-off (Architecture & Decisions)

1. **大腦選型 (Intelligence Engine)**
   - *明確約束*: **暫不使用本地端模型 (No Local Models, e.g., Ollama)**。
   - *核心方案*: 採用 **Antigravity AI (Gemini 3 系列, 如 Flash/Pro 等)** 作為唯一的多模態分析大腦。
   - *優勢論證*: 無需消耗本地 GPU 資源、規避 OOM 風險、降低佈署成本；且最新一代 Gemini 具備極強的 GUI UI 語意理解能力，可準確辨識 Xilinx 複雜面板中的微小 Icon 與 TreeView。

2. **定位與控制層 (Vision to Actuation - 降維優化策略)**
   - *UIA 優先之混合引擎 (Hybrid RVA Engine)*:
     - **本地 UIA 快速路徑**: 優先嘗試利用 `pywinauto(backend="uia")` 找尋標準 Win32/UWP 控制項 (如 Xilinx 的標準按鈕)，實現毫秒級定位與操作，大幅降低 LLM 依賴與 API Token 成本。
     - **大腦指導定位 (Fallback)**: 若 UIA 樹解析失敗，觸發視窗截圖並透過 `aa-bridge` 呼叫 Vision Fallback。
   - *視覺 Prompt 座標正規化 (Normalized Coordinates)*:
     - 絕對不請求實體像素。嚴格要求 Gemini 以 JSON 回傳 `[0.0, 1.0]` 的正規化 `[ymin, xmin, ymax, xmax]` 邊界框。本地端收到後再乘以實體解析度計算點擊位置，徹底解決 Windows 高 DPI 縮放與偏移問題。
   - *聚焦式截圖 (Active Window Cropping)*:
     - 結合 `pywinauto` 獲取目標視窗 RECT 後，僅針對局部範圍截圖並執行灰階壓縮，避免全螢幕上傳浪費 Token 與干擾辨識精準度。
   - *抽象封裝 (MCP State Machine)*:
     - 所有 UIA、Vision Fallback、防抖動與安全審核將封裝為統一的 Antigravity MCP Server（提供如 `rva_click` 偽工具）。Agent 只需拋出意圖即可，由底層隔離繁瑣的座標計算。

3. **狀態閉環與快取機制 (Caching & Verification)**
   - **Click → Wait → Verify**: 任何自動化點擊後需驗證狀態變化，非僅靠時間盲等。
   - **畫面防抖動 (ImageHash Caching)**: 使用 `imagehash.dhash`，若擷取畫面與上一禎相比未變更 (小於 Threshold)，則不觸發 LLM 推理，節省 40~60% 以上不必要的 API 呼叫。
   - **非同步 Console 監控**: 捕捉 `Programming succeeded` 等日誌不再依賴反覆送圖。

## 🛡️ 資安與防護建模 (STRIDE & Failsafes)

針對實體的硬體燒錄與 GUI 操控，潛在風險 (Risk) 極高：
- **T (Tampering) & R (Repudiation)**: 需建立防竄改的 `RVA_AuditLog`。每次執行操作前，記錄當下截圖、時間點及即將執行的動作，以利事故追溯。
- **I (Information Disclosure)**: 避免螢幕擷取到無關之私密對話。在向 API 發送截圖前，盡可能利用 `pywinauto` 取得 Xilinx/Vitis 視窗的邊界範圍 (Bounding Box) 進行局部截圖，而非全螢幕上傳。
- **D (Denial of Service) & E (Elevation of Privilege)**: 自動化失控與高危險動作。
  *防禦*: 
  1. 啟用 `pyautogui.FAILSAFE = True` (滑鼠移至螢幕角落即物理中斷)。
  2. 設計人機協作閘道 (Human-in-the-Loop)：對於「抹除 Flash」、「燒錄 FPGA」等毀滅性或不可逆變更，強制跳出對話框要求人類確認 (Dry-run mode & UAC Bypass Prompt)。
  3. **雙重 Watchdog 與逾時防護 (Dual Kill-Switch)**：除全域熱鍵 (e.g., Ctrl+Esc) 直接斬斷 GUI 執行緒外，增加進度條卡死偵測 (如果 900 秒內進度 `%` 完全沒有變更或 Console 懸停，即觸發 `safe_abort` 系統中斷)。

## 📋 邊界定義與驗收標準 (DoD)

- [ ] 完成核心 `rva_engine.py` 開發，與 Antigravity Gemini 3 介接進行畫面理解。
- [ ] 支援針對特定目標的辨識與點擊 (例如：打開 Xilinx / Vitis 相關測試畫面並精準點擊特徵按鈕)。
- [ ] 實作全域緊急中斷機制 (Kill-Switch) 與畫面局部截圖功能。
- [ ] 產出可與 `uart2mcp` 協作的概念性腳本 (PoC)。
- [ ] 產出對應的 `PLAN.md` 規劃。

---
*Signed by Tom, Senior Architect. Prepared for /aa-plan 138.*

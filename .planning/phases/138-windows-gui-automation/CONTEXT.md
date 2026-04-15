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

2. **定位與控制層 (Vision to Actuation)**
   - *混合 RVA 引擎架構*:
     - **視覺截圖**: 使用 `mss` 進行極速跨平台螢幕擷取。
     - **大腦指導定位**: 將畫面傳給 Gemini Vision，透過 Prompt 獲取目標 UI (例如：Program Device 按鈕或 Console 面板) 的座標區塊。
     - **本地執行**: 收到大腦座標後，透過 `pyautogui` / `pywinauto` 驅動滑鼠點擊與鍵盤輸入。

## 🛡️ 資安與防護建模 (STRIDE & Failsafes)

針對實體的硬體燒錄與 GUI 操控，潛在風險 (Risk) 極高：
- **T (Tampering) & R (Repudiation)**: 需建立防竄改的 `RVA_AuditLog`。每次執行操作前，記錄當下截圖、時間點及即將執行的動作，以利事故追溯。
- **I (Information Disclosure)**: 避免螢幕擷取到無關之私密對話。在向 API 發送截圖前，盡可能利用 `pywinauto` 取得 Xilinx/Vitis 視窗的邊界範圍 (Bounding Box) 進行局部截圖，而非全螢幕上傳。
- **D (Denial of Service) & E (Elevation of Privilege)**: 自動化失控與高危險動作。
  *防禦*: 
  1. 啟用 `pyautogui.FAILSAFE = True` (滑鼠移至螢幕角落即物理中斷)。
  2. 設計人機協作閘道 (Human-in-the-Loop)：對於「抹除 Flash」、「燒錄 FPGA」等毀滅性或不可逆變更，強制跳出對話框要求人類確認。

## 📋 邊界定義與驗收標準 (DoD)

- [ ] 完成核心 `rva_engine.py` 開發，與 Antigravity Gemini 3 介接進行畫面理解。
- [ ] 支援針對特定目標的辨識與點擊 (例如：打開 Xilinx / Vitis 相關測試畫面並精準點擊特徵按鈕)。
- [ ] 實作全域緊急中斷機制 (Kill-Switch) 與畫面局部截圖功能。
- [ ] 產出可與 `uart2mcp` 協作的概念性腳本 (PoC)。
- [ ] 產出對應的 `PLAN.md` 規劃。

---
*Signed by Tom, Senior Architect. Prepared for /aa-plan 138.*

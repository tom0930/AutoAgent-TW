# Architectural Context: Phase 138 — Windows GUI Automation (RVA & Vision Integration)

## 🎯 任務目標與意圖挖掘 (Context & Intent)
相較於常規的 API 串接或網頁爬蟲 (如 Phase 139 的 biggoALL)，許多遺留的 Windows 原生應用程式或受嚴格反爬機制保護的沙盒應用，缺乏開放接口。
本階段的目標是建構一套具備「視覺感知 (Vision)」與「動態操作 (RVA - Robotic Vision Automation)」的自動化驅動引擎，使 Agent 能夠針對任意 Windows 視窗「看見畫面、理解元素、精準點擊」並將工作流模組化。

## 🛠️ 架構選型與 Trade-off (Architecture & Decisions)

要實作 Windows GUI 視覺自動化，必須具備三個層面的能力：

1. **視覺擷取層 (Capture Layer)**
   - *方案 A*: 依賴 `Pillow` 的 `ImageGrab`。 (簡單但效能較差)
   - *方案 B (首選)*: 使用 `mss` 進行極速跨平台螢幕擷取，搭配 `pygetwindow` 定位目標視窗範圍，減少全螢幕截圖導致的精準度下降。

2. **定位與理解層 (Vision / Recognition Layer)**
   - *方案 A*: OpenCV (Template Matching)。優點：速度快、不耗 Token。缺點：面對 UI 微調、解析度縮放 (DPI scaling) 容易失效。
   - *方案 B*: Multimodal Agent (直接將畫面傳入 Gemini/Claude 獲取座標)。優點：具備語意理解。缺點：Token 重、延遲高 (3s+)。
   - *方案 C (首選融合架構)*: **Hybrid RVA Engine**
     - 基礎操作與重複性高/靜態的元素：以 OpenCV Template Matching + Text OCR (如 Tesseract 或快速 OCR API) 定位。
     - 複雜或非預期畫面：觸發 Fallback 呼叫 Vision LLM 進行語意分析與除錯。

3. **控制層 (Actuation Layer)**
   - 採用 `pyautogui` 專責鍵盤/滑鼠自動化，並搭配防呆機制。

## 🛡️ 資安與防護建模 (STRIDE & Failsafes)

針對實體 GUI 操控，風險遠高於一般 Backend API：
- **T (Tampering) & R (Repudiation)**: 需建立 `AuditLog`。每次執行操作前，記錄當下截圖、時間點及即將執行的動作，以利追溯。
- **I (Information Disclosure)**: 由於會擷取螢幕，可能有高度機密資訊 (如密碼、對話) 入鏡。
  *防禦*: 截圖檔案僅存放在不可 Commit 的 Buffer (`scratch/tmp_vision/`) 且不應傳輸至未受信任的第三方，若需送往 Vision LLM 應套用 Privacy Mask 或僅截取局部 Region。
- **D (Denial of Service - Automation Runaway)**: 自動化失控 (例如滑鼠狂點導致無法關閉)。
  *防禦*: 
  1. 啟用 `pyautogui.FAILSAFE = True` (滑鼠移至螢幕角落即中斷)。
  2. 設計全域緊急中斷快捷鍵 (Global Kill-Switch Shortcut，如 `Ctrl+Esc`)。

## 📋 邊界定義與驗收標準 (DoD)

- [ ] 完成核心 `rva_engine.py` 開發，封裝截圖、等待、點擊及文字輸入等功能。
- [ ] 支援基於圖片特徵的「等待並點擊 (Wait-and-Click)」功能。
- [ ] 實作緊急中斷機制 (Kill-Switch) 與自動防呆 (Failsafe)。
- [ ] 能通過一個完整的 E2E 模擬場景 (例如：自動打開記事本，從螢幕辨識它，輸入一段文字並存檔)。
- [ ] 加入 `.planning/` 與系統架構文檔更新。

## 🏗️ 編排策略 (Orchestration)
- **Mode**: Multi-Agent 逐步構建 (Phase 分離實作)。
- **Step 1**: 基礎 RVA 封裝與本機測試。
- **Step 2**: 融合 Vision OCR / OpenCV。

---
*Signed by Tom, Senior Architect. Prepared for /aa-plan 138.*

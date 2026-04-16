# Phase 117 Plan: 架構師審計與自動化流程深度整合 (aa-cc-link)

## 🛡️ Objective: 穩定性優先的實作規劃
依據 `CONTEXT.md` 確立的 Hybrid 模式，將建置「AA -> CC 通訊介面」拆解為具有防禦性、可獨立測試的原子任務。

## 🌊 Task Breakdown

### Wave 1: 基礎通訊層建置 (Core Link)
- [ ] **[任務 1.1]**：開發 `cc_manager.py` (放置於 AutoAgent 腳本目錄)。
  - **規格**：使用嚴格 Python 3.10+ Type Hints (如 `Dict`, `Optional`)。
  - **功能**：掃描 `.planning/phases/XXX/QA-REPORT.md` 是否存在，以及掃描 `STATE.md` 掌握當前 Phase 進度。
  - **風險**：低風險，確保不引用外部非標準函式庫。

### Wave 2: AA 流程改造 (Workflow Injection)
- [ ] **[任務 2.1]**：修改 `aa-progress.md` 工作流。
  - 在輸出進度時，呼叫 `cc_manager.py --check-audit`，若該 Phase 實作完畢但無審計報告，顯示「需要架構師審核」。
- [ ] **[任務 2.2]**：修改 `aa-ship.md` 工作流。
  - 作為最後一道防線，若偵測無 CC 審核授權，拋出強烈黃色警告字眼：「建議進行 `/cc-qa N` 以確診程式碼品質」。

### Wave 3: 整機驗證與防呆重構
- [ ] **[任務 3.1]**：建立虛擬的 Phase 模擬測試。
  - 使用指令產生錯誤（如不帶 RAII 的 C++ 碼），驗證 `aa-ship` 加上 `cc_manager.py` 是否能精準攔截。
- [ ] **[任務 3.2]**：根據測試結果修補所有 Edge Cases（例如：`.planning` 目錄不存在的極端狀況）。

## 📈 Performance & Risk Audit
所有的檢查邏輯需保證在 100ms 內執行完畢，避免拖累原有 AA 流程的順暢度。`cc_manager.py` 的讀寫需做好防呆機制。

> *Generated via `/cc-plan 117` utilizing Antigravity Code Consultant.*

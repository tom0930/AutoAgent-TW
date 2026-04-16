# Task 3: Orchestrator Integration & Job Object

## 🎯 目標
將視覺引擎完美無縫地整合進主流程，並加上最後一道安全防線。

## 📋 具體步驟
1. [ ] **封裝 Python Context Manager**：
   - 建立 `src/core/rva/vision_context.py`。
   - 實作 `with VisionEngine.active(fps=2):` 語法，自動處理喚醒與自動休眠。
2. [ ] **防禦性生命週期實作 (Job Object)**：
   - 修改 `src/core/orchestration/spawn_manager.py`。
   - 在啟動 PyRefly 時，建立 `win32job.CreateJobObject` 並將其加入。
3. [ ] **整合至 `coordinator.py`**：
   - 在執行視覺相關 Task 節點前，由 Supervisor 自動開啟 Context。
4. [ ] **災難恢復測試**：
   - 暴力 Kill 掉 Antigravity 主進程，驗證 PyRefly 是否同步消失。

## 📄 預期變更文件
- `src/core/rva/vision_context.py`
- `src/core/orchestration/coordinator.py`
- `src/core/orchestration/spawn_manager.py`

## ✅ 驗證標準 (UAT)
- 資源回收率 100%：手動關閉測試工作區後，背景無殘留任何相關進程。
- Agent 行為正常：在 `with` 區塊內能夠正確抓取並識別螢幕元素。

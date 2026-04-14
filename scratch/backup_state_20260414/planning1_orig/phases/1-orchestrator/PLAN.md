# 執行計畫 (PLAN) - Phase 1: 子代理系統與平行任務調度 (v1.9.0)

## 架構設計與變更範圍
- **新增**: `scripts/subagent/spawn_manager.py` (管理非同步 API 呼叫的子代理程式生命週期)
- **新增**: `scripts/subagent/coordinator.py` (負責任務拆解、結果彙整與動態排程)
- **修改**: `scripts/aa_chain_orchestrator.py` (重構或擴充以支援 `aa-orchestrate` 入口指令)
- **相依性**: 更新 `requirements.txt` 加入 `anthropic` SDK 以備呼叫。

---

## 執行 Wave 拆解

### Wave 1: 基礎子代理框架建立
**目標**: 實作 `SubagentSpawnManager` 用於 LLM 子代理管理，確保基本的非同步呼叫與超時處理。
1. 更新 `requirements.txt` (加 `anthropic`)。
2. 建立 `scripts/subagent/` 目錄。
3. 實作 `spawn_manager.py`，定義 `SubagentSpawnManager` 類別，提供 `spawn(task_spec)`, `collect(subagent_id)`, `parallel(task_specs)` 介面。
4. 防呆檢查：針對 LLM API 回應設計重試機制、除錯 (debug printf) 與逾時控制 (asyncio.wait_for)。

### Wave 2: 協調器任務拆解引擎
**目標**: 實作 `Coordinator`，利用 `anthropic` API 解析使用者提供的高階目標，拆分為子代理的 `[Research, Implement, Verify]` 任務規格。
1. 實作 `coordinator.py`。
2. 開發 `_decompose(goal)`: 讓 LLM 將輸入切分成 JSON Array 的 `task_spec`。
3. 開發 `orchestrate(goal)`: 循序觸發 Research -> (綜合整理成果) -> Implement -> Verify 三大流程。
4. 加入對各子代理成果的 JSON 解析，整合為最終大計畫或執行結果報告。

### Wave 3: 使用者指令與外部整合
**目標**: 新增 `/aa-orchestrate` CLI 命令並擴大與原本系統的相容。
1. 新增 `scripts/aa_orchestrator.py` (或是更新現有 chain orchestrator) 來接收指令與目標參數。
2. 將指令接上 `Coordinator.orchestrate`。
3. 輸出：以豐富的前端格式輸出目前各個 Subagent 正在執行哪些部分 (Logging / Debug Info)。
4. (Optional) 將子代理狀態的寫入與 Dashboard (Port 9999) 機制連接，如果 `.agent-state/scheduled_tasks.json` 有關聯則更新狀態。

---

## 驗證標準 (UAT Criteria)
- [ ] 能在背景非同步觸發最少兩個 `Research` 子任務，並各自不阻塞地返回正確長文檔。
- [ ] 執行 `/aa-orchestrate "優化登入效能"`，系統自動生成至少 3 個獨立子代理的任務分工並依次執行驗證。
- [ ] 每一次 API 呼叫、子任務發出與接收都具備完整的 log (Debug Printf)。
- [ ] 出現 API 錯誤或逾時，子代理能妥善回報失敗給 Coordinator，而不是拋出未捕捉的 Exception 讓整個主程式當機。

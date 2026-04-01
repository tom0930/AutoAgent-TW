# AutoAgent-TW Worker-Orchestration 架構設計書 (v1.8.0-Draft)

## 1. 核心理念：解耦與派遣 (Decouple & Dispatch)

為了提升大型專案的開發效率，`AutoAgent-TW` 將從「單一執行模組」進化為「協調器 (Coordinator) - 執行工 (Worker)」模式。

### 角色定義：
- **Coordinator (主 Agent)**：負責解析 `ROADMAP.md`、制定 `PLAN.md`、管理全局上下文、最終審核與 Commit。
- **Worker (子執行工)**：負責單一 `Task` 的執行、局部代碼讀寫、單元測試、產出 XML 格式結果報告。

---

## 2. 工具連動：`/aa-execute` 2.0 流程

### Phase A: 規劃與規格化 (Synthesis)
主 Agent 在讀取 `PLAN.md` 後，針對每個 Wave 中的 Task 產出一個「極簡化」的規格書 (Spec)。
- **包含**：
  - 精確變動路徑：`src/auth.py`, `tests/auth_test.py`
  - 核心邏輯修改指引
  - 驗證條件 (UAT)

### Phase B: 子行程派遣 (Worker Spawning)
利用 `aa-spawn` 指令（概念中）同步或異步啟動多個 Worker 進程。
- **上下文隔離**：Worker 只會載入當前任務相關的一小部分檔案，避免 Token 過載、提升反應速度。

### Phase C: XML 結構化回報
Worker 完成後，必須回傳以下格式的 XML 片段給 Coordinator：
```xml
<task-notification>
  <task-id>w-auth-01</task-id>
  <status>completed|failed</status>
  <summary>修正了 auth.py 第 42 行的空指標錯誤</summary>
  <usage>
    <tokens>1250</tokens>
    <files_modified>2</files_modified>
  </usage>
  <result>所有認證測試均已通過 (Pass: 12/12)</result>
</task-notification>
```

---

## 3. 並行處理與衝突防範 (Concurrency Control)

為了防止多個 Worker 同時修改同一檔案：
1. **讀寫鎖 (RW-Lock)**：主 Agent 在派遣時，會檢查各 Worker 的檔案路徑有無交集。
2. **無交集並行**：路徑無重疊的 Task (例如：修復 UI 與優化 DB) 將同時併行。
3. **路徑重疊隊列**：路徑重疊的 Task 會自動轉為序列化執行，保證安全性。

---

## 4. 下一階段優化 (Roadmap)

1. **LSP 輔助定位**：Worker 可調用 LSP 獲取全專案 Symbol 定義，無需加載整個 Codebase。
2. **自動 Git Stash**：Worker 在失敗時應具備自動「暫存/還原」代碼的能力，不污染工作區。
3. **TUI 進度條**：在 Dashboard 呈現每個正在跑的 Worker 的即時百分比。

---
*Drafted by ProblemSolver@AutoAgent-TW v1.7.2 - 2026-04-01*

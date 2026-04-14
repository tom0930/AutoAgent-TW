# CONTEXT: Phase 3 — 工作流客製化系統 (Workflow Customization System)

## 📌 1. 背景與動機 (Background)
AutoAgent-TW 目前的指令與工作流主要為硬編碼 (Hardcoded)，缺乏靈活性。
Claude Code 的 `CLAUDE.md` + 自訂 Skills + Hooks 機製證明了開發環境客製化的強大能力。
本階段目標是將此彈性引入 AutoAgent-TW，讓團隊能根據專案規範自動約束 AI 行為，並擴充自訂技能。

## 🎯 2. 核心目標 (Core Objectives)
1.  **專案規範注入**：從 `CLAUDE.md` 自動提取架構、風格與測試約束。
2.  **技能動態掛載**：掃描 `.agents/skills/` 並將 Markdown 格式的技能轉化為可用指令。
3.  **生命週期鉤子**：在工具調用前後、Commit 前後觸發自訂邏輯 (如 Lint/AutoFix)。
4.  **指令化管理**：新增 `/aa-skill` 與 `/aa-hook` 指令。

## 🛠️ 3. 技術決策 (Design Decisions)

### 3.1 規範層：`CLAUDE.md`
*   **機制**：系統啟動或 `aa-discuss` 時自動讀取項目根目錄的 `CLAUDE.md`。
*   **注入方式**：將其內容作為 `System Prompt` 的一部分，確保 AI 遵循特定專案的 Coding Style 與測試要求。

### 3.2 技能層：`SkillLoader`
*   **儲存位置**：`.agents/skills/*.md`
*   **格式**：Markdown 標題 (## 執行步驟) + YAML Frontmatter (metadata)。
*   **處理器**：
    *   `discover()`：異步掃描目錄。
    *   `register()`：解析觸發詞 (Trigger) 並映射至內部調用路徑。

### 3.3 執行層：`HookManager`
*   **事件列表**：
    *   `PreToolUse` / `PostToolUse`
    *   `PreCommit` / `PostCommit`
    *   `OnTaskComplete` / `OnBudgetExceed`
*   **配置**：`.agents/hooks.json` 儲存事件與對應 Action (Command/Skill/Notify) 的映射。
*   **條件篩選**：支援基於 `file_path` 或 `tool_name` 的正則匹配。

### 3.4 指令集 (CLI)
*   `/aa-skill list/create/test`
*   `/aa-hook list/add`

## 📊 4. 影響範圍 (Impact)
*   `scripts/scheduler_daemon.py`：需在啟動循環中加入 Loader 初始化。
*   `_agents/workflows/`：可進一步精簡，或轉換為客製化 Skills。
*   `Dashboard`：需新增面板監視 Hook 的觸發歷史與 Skill 狀態。

## 🚀 5. 下一步建議
1.  執行 `/aa-plan 3` 以產出具體的檔案路徑與開發計畫。
2.  初始化 `CLAUDE.md` 範本以驗證注入效果。

---
**核定日期**: 2026-04-02
**負責人**: Antigravity (AA-Consultant)

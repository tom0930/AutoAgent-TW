# PLAN: Phase 3 — 工作流客製化系統 (Workflow Customization System)

## 📌 執行計畫概覽 (Overview)
本計畫將把硬編碼的工作流升級為可客製化的掛載系統，包括 `CLAUDE.md` 規約注入、Markdown 技能加載與動態 Hook 綁定。

---

## 🌊 Wave 1: 異步生命週期鉤子系統 (HookManager Refactoring)
*   **目標**: 使 Hook 能根據配置動態執行自訂指令，不再硬編碼。

### 任務清單:
1.  **[Task 1.1]** 建立 `.agents/hooks.json` 初始配置檔案。
    *   *Step*: 範例配置應包含 `PostToolUse` 的 `ruff` 格式化 Hook。
2.  **[Task 1.2]** 重構 `scripts/hooks/hook_manager.py`。
    *   *Step*: 新增 `load_config()`。
    *   *Step*: 在 `trigger()` 中檢查並執行配置中的命令。
    *   *Step*: 加入變數替換 (如 `{file_path}`)。
3.  **[Task 1.3]** 新增重入保護機製 (Re-entry Guard)。
    *   *Step*: 確保 Hook 調用的子工具不會再次無限觸發 Hook。

---

## 🌊 Wave 2: 技能引擎優化 (SkillLoader Implementation)
*   **目標**: 從 `.agents/skills/*.md` 動態加載並執行技能。

### 任務清單:
1.  **[Task 2.1]** 建立 `scripts/skills/skill_loader.py`。
    *   *Step*: 實作 Markdown 解析邏輯（提取 YAML Frontmatter）。
    *   *Step*: 將技能映射到系統可用指令列表中。
2.  **[Task 2.2]** 整合到 `scheduler_daemon.py`。
    *   *Step*: 在啟動時自動調用 `loader.discover()`。
3.  **[Task 2.3]** 支援 `/aa-skill list` 與 `/aa-skill test <name>`。

---

## 🌊 Wave 3: 項目規約注入 (CLAUDE.md Integration)
*   **目標**: 使 `CLAUDE.md` 成為專案的行為手冊。

### 任務清單:
1.  **[Task 3.1]** 建立 `scripts/config/claude_loader.py`。
    *   *Step*: 偵測專案根目錄是否具備 `CLAUDE.md`。
    *   *Step*: 將文本格式化為 Prompt 片段。
2.  **[Task 3.2]** 注入系統上下文。
    *   *Step*: 修改 LLM 調用入口，將 `CLAUDE.md` 內容附加在對話起始的 System Message 中。

---

## 🌊 Wave 4: 測試與管理指令 (Validation & CLI)
*   **目標**: 最終驗證與提供管理工具。

### 任務清單:
1.  **[Task 4.1]** 實作 `/aa-hook` 工具。
    *   *Step*: 提供 `list` / `add` 操作。
2.  **[Task 4.2]** UAT 驗證流程。
    *   *Step*: 驗證 `CLAUDE.md` 規則是否被遵循（如限制 API 路徑）。
    *   *Step*: 驗證 `hooks.json` 是否準確觸發 Lint。

---

## ✅ 驗證標準 (UAT Criteria)
1.  **UAT-01**: 能通過 `/aa-skill list` 看到 `.agents/skills/` 下所有技能的描述。
2.  **UAT-02**: 修改 `.py` 檔案後，`PostToolUse` Hook 能成功執行 `ruff check` 並完成自動修復。
3.  **UAT-03**: 如果在 `CLAUDE.md` 中禁止使用 `any` 類型，AI 在生成的 TypeScript 代碼中應不再出現 `any`。

---
**日期**: 2026-04-02
**負責人**: Antigravity (AA-Consultant)

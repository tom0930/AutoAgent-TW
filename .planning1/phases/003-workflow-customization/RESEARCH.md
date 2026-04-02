# RESEARCH: Phase 3 — 工作流客製化系統

## 1. 實施方案分析 (Implementation Analysis)

### 1.1 `CLAUDE.md` 規範注入
*   **現狀**: 目前 AI 的系統提示詞 (System Prompt) 是靜態的或由 Skill 定義。
*   **方案**: 在 `scripts/scheduler_daemon.py` 加載階段，讀取 `CLAUDE.md` 並封裝為 `ProjectContext` 對象。
*   **優點**: 無需修改核心引擎即可變更 AI 行為。

### 1.2 `SkillLoader` 模式
*   **核心功能**: 將 `.agents/skills/*.md` 視為動態指令。
*   **解析器**: 使用正則表達式或輕量級 Markdown 解析器提取 YAML Frontmatter (`trigger`, `description`)。
*   **執行路徑**: 當使用者輸入 `/skill_name` 時，Agent 讀取對應 MD 並將其作為指令執行。

### 1.3 `HookManager` 擴展
*   **現狀**: `scripts/hooks/hook_manager.py` 目前僅硬編碼了預測引擎的調用。
*   **方案**: 
    1. 引入 `.agents/hooks.json` 配置。
    2. 使用 `subprocess.run` 或 `os.system` 執行配置中的 `command`。
    3. 支援 `{{file_path}}` 等變數替換。

## 2. 依賴檢查 (Dependency Check)
*   **Python 內置庫**: `json`, `re`, `pathlib`, `subprocess` (已滿足)。
*   **第三方庫**: 目前不打算引入額外的 Markdown 庫，使用字串處理與 `re` 即可保持系統輕量。

## 3. 已識別的陷阱 (Pitfalls)
*   **循環調用**: 如果 Hook 觸發了會再次觸發 Hook 的操作（例如 `PostToolUse` 觸發 `write_file` 而 Hook 監聽 `write_file`），會導致無限循環。
    *   *對策*: ใน `HookManager.trigger` 中加入重入保護 (Re-entry Guard)。
*   **權限問題**: `CLAUDE.md` 中如果定義了危險規則，可能被 AI 誤解。
    *   *對策*: 在 System Prompt 中明確區分「約束（Constraints）」與「執行動作（Actions）」。

---
**日期**: 2026-04-02
**研究員**: Antigravity

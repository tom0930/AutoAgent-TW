---
description: Context History & Memory Management / 歷史上下文持久化與記憶檢索管理
---

# AutoAgent-TW: `/aa-history` Workflow

此 Workflow 處理「上下文腐化 (Context Rot)」與「AI 失憶」問題。使用基於檔案系統的三層記憶架構。

## 引數解析

使用者呼叫方式可能為：
1. `/aa-history init [project_basename]`
2. `/aa-history update`
3. `/aa-history search [keyword]`

// turbo-all

## Steps

### Step 1: 解析使用者意圖與路徑判斷

1. 若為 `init [project_basename]`：
   - 使用 `run_command` 確認 `mkdir -p .context-[project_basename]/archives`。
   - 使用 `run_command` 將 `templates/core_template.md` 複製至 `.context-[project_basename]/core.md`。
   - 建立空的 `.context-[project_basename]/current.md` 和 `.context-[project_basename]/changelog.md`。
   - 結束流程並告知用戶初始化完成。

2. 若為 `update`：
   - 呼叫 `python scripts/auto_summarizer.py --file .context-[project_basename]/current.md` 執行自動摘要。
   - 分析摘要結果與當下 `.planning/STATE.md`。
   - 若為重大里程碑，則手動呼叫 MCP 工具 `memory::save` 以結構化方式歸檔：
     `memory::save(content="...", title="Phase Summary", tags="milestone", importance=4)`。
   - 更新 `.context-[project_basename]/changelog.md`。
   - 整理後的內容移至 `archives/` 下的日期檔案。
   - 重置 `.context-[project_basename]/current.md`。

3. 若為 `search [keyword]` (預設查詢行為)：
   - **優先呼叫 MCP 工具 `memory::query(keyword)`** 獲取結構化與全文檢索結果。
   - 若 MCP 回傳不足，使用 `grep_search` 遞迴掃描 `.context-[project_basename]/`。
   - 將檢索到的歷史決策、重疊架構與相關開發經驗彙整，提供給使用者。
   - 如果遇到類似 bug，一併引用過去的解法。

### Step 2: 上下文對齊 (Context Alignment)
- 如果剛執行完 `search`，請向使用者總結找回的歷史記憶，並詢問：
  > "是否需要根據這些歷史上下文，更新目前的任務計畫或直接開始執行下一步 (如 `/aa-plan` 或 `/aa-helper`)？"

### Step 3: 注意事項
- 嚴禁把 `autoagent-TW/temp` 中的垃圾檔案當作核心 Context。
- 始終以 `.context-[project_basename]/core.md` 內容為該專案的唯一最高執行憲法（含測試與安全要求）。

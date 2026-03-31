# Phase 4 Context: Task Chaining & Pipelines

## Goals
讓使用者能自定義複雜的任務序列 (Pipelines)，並支援基本的條件執行邏輯。

## Design Decisions

### 1. Simple Orchestrator (`aa_chain.py`)
- **Decision**: 建立一個解析器，將字串（如 `"A | B | C"`) 轉換為循序執行的工作流。
- **Status Support**: 每一小步都會更新同步至 Dashboard。

### 2. Conditional Logic
- **Decision**: 支援特定的關鍵字：
  - `&&`: 只有上一步成功 (Exit Code 0) 才繼續。
  - `||`: 只有上一步失敗才執行 (Error Recovery)。
  - `|`: 不論上一步結果，強制繼續。

### 3. Syntax Example
- `/aa-chain "git pull && aa-qa || aa-fix"`
- 如果 `git pull` 成功，執行 `aa-qa`。如果 `aa-qa` 失敗，啟動 `aa-fix`。

## Next steps
- `/aa-plan 4`

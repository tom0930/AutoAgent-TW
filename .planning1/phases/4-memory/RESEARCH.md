# Phase 4: 專案記憶與上下文管理 (Memory & Context Management) - RESEARCH

## 領域研究
根據 `newplanning.md` 與使用者需求，AutoAgent-TW 需要具備持久化記憶機制，解決每次對話/啟動都是零狀態的問題。

### 目標
建立分層記憶體系：
1. **L1 (Session)**：當前對話，存於 `.agent-state/session_memory.json`
2. **L2 (Project)**：專案持久記憶，存於 `.agent-state/project_memory.json`
3. **L3 (Global)**：全域通用記憶，存於 `~/.autoagent/global_memory.json`

### 使用者新增需求
1. **List 記憶**：可列出目前全部或指定層級的記憶。
2. **Delete 記憶**：可選擇性刪除不需要的記憶。
3. **Focus 記憶**：專注於某特定記憶，忽略其他記憶，確保 AI 只存取特定的開發上下文。

### 架構設計
- `scripts/memory/memory_store.py`: 核心資料存儲與向量/標籤檢索引擎。每個記憶擁有唯一 ID (UUID)。
- `scripts/memory/context_compressor.py`: 用於 L1 會話壓縮機制。
- `scripts/aa_memory.py`: CLI 工具，提供 `list`, `add`, `delete`, `focus`, `export` 選項。

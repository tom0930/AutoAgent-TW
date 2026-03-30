# Phase 2 Context: Dynamic Execution Tree & Indicators

## Goals
實現動態 Mermaid 執行樹，將 `.planning/ROADMAP.md` 的靜態開發路徑轉換為即時更新的互動式流程圖。

## Design Decisions

### 1. Visualization Engine
- **Decision**: 使用 Mermaid.js (透過 CDN)。
- **Rationale**: 開發效率最高，直接支持文字轉圖表，完美結合 `status.html`.

### 2. Roadmap Mapping
- **Decision**: 建立一個新腳本 `scripts/roadmap_parser.py` 負責解析 `ROADMAP.md` 並產出 Mermaid 格式字串。
- **UI Logic**:
    - `DONE`: 節點變綠色。
    - `RUNNING`: 節點變綠色且閃爍 (Pulse)。
    - `PENDING`: 節點變灰色。
    - `FAIL`: 節點變紅色。

### 3. State update
- **Decision**: `status_state.json` 將新增一個 `mermaid_code` 欄位。
- **Rationale**: 前端 `status.html` 只需要讀取該字串並呼叫 `mermaid.render()` 即可，不需要在前端處理複雜解析。

## Next steps
- /aa-plan 2

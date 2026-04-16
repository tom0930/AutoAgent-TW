# Phase 146: Data Specialist & Long-term Memory Integration

## 1. 核心核心目標
建立具備數據感知能力與長期專案記憶的子系統，針對大型 JSON/CSV (FPGA Register Map) 進行優化。

## 2. 代碼實施細節
- **fs-token-killer**: 使用 RTK 進行數據結構採樣 (Sampling)。
- **memory-mcp**: 基於 JSON 的層級化存儲，預計放置於 .agents/memory/。
- **sequential-thinking**: 引入執行前推理鏈機制。

## 3. 資安約束
- **禁止記憶範圍**: .env, *.key, *.token, scratch/。
- **存取限制**: 僅限於當前工作空間的 root-level 讀取。

## 4. 路由整合
需同步更新 mcp-router.toml 以對接上述新工具。

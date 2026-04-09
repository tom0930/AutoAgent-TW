# CONTEXT: Phase 128 — Persistent Memory System (L1/L2/L3 MemoryStore)

## 🎯 核心目標
徹底解決 AI Agent「上下文腐敗 (Context Rot)」與「記憶力流失」的痛點，從早期的手動 Workflow 升級為**程式化的原生記憶管理中心**。賦予系統自動壓縮、智慧歸檔以及讓 Agent 具備主動查閱過往記憶（MCP 整合）的能力。

---

## ✅ 最終技術決策

### 1. 儲存與檢索引擎：【純文本 + Metadata 輕量索引】 (1A)
*   **決策**: 保持 `.context` 目錄結構與 Markdown 純文本，搭配 Regex/Grep/Ripgrep 作為底層引擎。
*   **強化設計 (Metadata Indexing)**: 在 `.context/archives` 或 `knowledge` 中引入 `index.md` 或 `metadata.json`。記錄每個歸檔的：`Tags`、`Phase`、`關鍵決策`、`最後更新時間` 與 `重要性評分(1-5)`。
*   **未來擴展性 (Forward Compatibility)**: 不立刻使用 FAISS，但 Metadata 的設計為日後切換至 SQLite (FTS5) 或 sqlite-vec (Keyword + Vector Hybrid) 鋪好一鍵無痛升級的路。

### 2. Agent 介接模式：【專屬 MCP 工具為核心，輔以防呆攔截】 (2A)
*   **決策**: 實作並暴露專屬的記憶器 MCP Server (`memory_server.py`)。
*   **MCP Tools 定義**:
    *   `memory::query(keyword)`: Agent 自動查閱專案歷史或全局 SOP。
    *   `memory::save(content, tags, importance)`: 允許 Agent 主動提煉有價值的結論存入長期記憶。
*   **防呆攔截 (Pre-flight Injection)**: Context Guard 在啟動階段，只會輕度把命中率最高的 L3 條款（例如安全鐵律）注入最前面，其餘一律依靠 Agent 自行呼叫 MCP 取回，避免 Prompt 過早超載。

### 3. L1 記憶體汰換與壓縮策略：【滾動視窗 + 小模型自動摘要】 (3B)
*   **決策**: 當 L1 (`current.md`) 的 Token 突破特定閾值（如 8k~12k）時，觸發背景自動壓縮機制 (Auto-Summarization)。
*   **壓縮邏輯 (Rolling Window)**:
    *   **舊區塊壓縮**: 呼叫低延遲/低成本小模型 (Gemini 1.5 Flash)，將上半部歷史結構化合併（產出 JSON: `progress`, `key_facts`, `decisions`, `open_items`）。
    *   **新區塊保留**: 留下最新的 30%~40% 原文詳細流程，維持推理精準度。
    *   **自動轉生**: 將摘要寫入 L2 (Project Memory)，並在 `current.md` 最上方留下一行 `[引用: 已歸檔至 archives/xxx.md]`，做到使用者與 Agent 皆無感切換。

### 4. 監控與透明化 (擴充設計)
*   實作 CLI 指令 `/aa-memory status` 或是 `memory::get_status` MCP 工具，輸出當下 L1/L2 的 Token 佔用率與最新歸檔情況，確保維護成本透明可控。

---

## 📁 預期新增/修改檔案規劃

| 檔案路徑 | 功能目標 | 關聯步驟 |
|----------|----------|----------|
| `scripts/memory_server.py` | 實作 MCP FastMCP Server (提供 `memory::query`, `memory::save`) | Task 1 |
| `scripts/auto_summarizer.py` | 實作 L1 Rolling Window 智慧壓縮機制 (調用 Flash 模型) | Task 2 |
| `scripts/context_guard.py` | (修正) 增加 Pre-flight Token 檢查與極輕量 L3 注入 | Task 3 |
| `.agents/skills/aa-memory/*` | 增加 user CLI 指令對應的 Workflow (供 `status` 查看) | Task 3 |
| `src/core/mcp_registry.py` | (修正) 將 memory server 掛載進入 Sub-Agent MCP 統一節點 | Task 1 |

---

## ⏱️ 估計與驗證 (UAT Criteria)
*   **UAT 1 (檢索)**: Agent 可以在沒有直接 Prompt 提示下，遇到特定 Error 時，自主呼叫 `memory::query` 並查獲預埋的解決方案。
*   **UAT 2 (自動壓縮)**: 人工塞入 12k Token 的垃圾紀錄至 `current.md`，系統能自動啟動 Gemini Flash，將上半部淬鍊為 1k Token 內的 JSON 摘要，且不會丟失核心架構結論。

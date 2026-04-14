# AGENT_DESIGN: Persistent Memory System (L1/L2/L3)

## 🧠 記憶體設計哲學
AutoAgent-TW 採用「漸進式遺忘與永恆歸檔」機制，確保 Agent 在長期的開發任務中不會因為 Token 溢出而失憶。

---

## 🏛️ 三層記憶體架構

### L1: Working Memory (`current.md`)
*   **定位**: 當前 Phase 的即時執行日誌。
*   **容量**: 閾值 **50,000 Tokens** (適配 Gemini 3 Flash)。
*   **管理**: 由 `auto_summarizer.py` (Sentinel Mode) 監控。
*   **溢出處理**: 委派 Antigravity 進行智慧摘要並寫入 L2，重置 L1。

### L2: Project Memory (`archives/`)
*   **定位**: 專案層級的決策歷史與里程碑。
*   **儲存**: 以 `YYYY-MM-DD_title.md` 格式存放。
*   **索引**: `metadata.json` 記錄標籤、重要性與時間戳。
*   **存取介面**: MCP `memory::query` ( ripgrep 全文檢索)。

### L3: Global Memory (`knowledge/`)
*   **定位**: 跨專案的全局智慧（SOP、除錯地圖、核心憲法）。
*   **來源**: 鎖定 `Knowledge Item (KI)` 系統。
*   **注入策略**: 由 `Context Guard` 在預飛行 (Pre-flight) 階段進行「最小化注入」。

---

## 🛠️ 開發者操作指南

### 1. 檢索歷史 (回憶)
欲查詢過往決策時，請子代理呼叫：
```python
memory::query(keyword="重構規則")
```

### 2. 手動歸檔 (刻骨銘心)
若發現一項極具價值的解決方案，請立即存入記憶：
```python
memory::save(content="...", title="SQLi 防禦策略", tags="security", importance=5)
```

### 3. 查看狀態
查看目前記憶體佔用與歸檔情況：
```bash
python scripts/memory_monitor.py
```

---

## ⚠️ 異常處理 (Sentinel Returns)
若 `Context Guard` 回報 `[OVERLOAD]`，Agent 必須停止當前計畫，優先執行「記憶壓縮任務」，產出摘要後再繼續，以避免 Context Rot。

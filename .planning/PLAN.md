# Phase 165 Plan: Subagent Resource Governance (v3.5.3)

## 1. 任務目標 (Objectives)
實現對子代理 (Sub-agents) 的精細化資源管控，防止資源耗盡與進程殘留。

## 2. 需求與邊界 (Requirements & Boundaries)
- **CPU 限制**：限制單個 Agent 的 CPU 權重或頻率。
- **Memory 限制**：根據 Role 分配記憶體配額 (General: 512MB, Expert: 2GB)。
- **TTL 機制**：任務超時自動回收。
- **監控回報**：即時回報資源佔用至 `.agent-state/`。

---

## 3. 波次實作計畫 (Implementation Waves)

### Wave 1: 強化 `win32_job.py` (基礎設施升級)
- [ ] 支援 `JOB_OBJECT_LIMIT_CPU_RATE_CONTROL`。
- [ ] 實作 `set_process_quota(pid, mem_limit, cpu_rate)` 函數。
- [ ] 優化錯誤處理，防止 Win32 API 權限不足導致的崩潰。

### Wave 2: 升級 `spawn_manager.py` (邏輯集成)
- [ ] 在 `AgentProcess` 中引入 `AA_AGENT_TTL` 邏輯。
- [ ] 修改 `spawn()`，根據 `role` 從 `subagents.json` 讀取 `quota` 並調用 `win32_job`。
- [ ] 實作基於 `threading.Timer` 的 TTL 自動終止機制。

### Wave 3: 資源監控與回報 (可視化與守護)
- [ ] 建立 `ResourceMonitor` 線程，每 5 秒掃描一次 `_ACTIVE_SUBAGENTS`。
- [ ] 統計數據寫入 `.agent-state/subagents/{id}.json`。
- [ ] 擴展 `HarnessCLI` (aa-harness status) 以顯示資源佔用。

---

## 4. 8 維度檢查 (GSD v2.1)

| 維度 | 說明 |
| :--- | :--- |
| **1. 需求拆解** | CPU (Rate), Memory (Quota), Time (TTL), Monitoring |
| **2. 技術選型** | `win32job` (Hard limits), `psutil` (Monitoring), `threading` (Heartbeat) |
| **3. 系統架構** | 垂直擴展 `orchestration` 模組，新增 `ResourceMonitor` 組件 |
| **4. 並行設計** | 監控線程採用非阻塞模式，使用 `threading.Event` 進行優雅停機 |
| **5. 資安設計建模** | 防止惡意 Prompt 構造大數據結構導致的 Memory DoS |
| **6. AI 產品考量** | 向用戶反饋 "Resource Limited" 狀態，而非直接顯示 Python Error |
| **7. 錯誤處理** | 處理 `AccessDenied` (OpenProcess) 與 `LimitExceeded` 異常 |
| **8. 測試策略** | `tests/test_governance.py`: 模擬死循環進程並驗證是否被 Job Object 或 TTL 殺死 |

---

## 5. 預計產出檔案 (Expected Artifacts)
- `src/utils/win32_job.py` (Updated)
- `src/core/orchestration/spawn_manager.py` (Updated)
- `src/core/orchestration/monitor.py` (New)
- `tests/test_governance.py` (New)

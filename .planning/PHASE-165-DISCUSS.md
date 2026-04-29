# Phase 165 Discussion: Subagent Resource Governance

## 1. 核心需求與目標 (Requirements & Goals)
在 Phase 164 實現了 **語境隔離 (Context Isolation)** 後，目前的子代理 (Sub-agents) 雖然在數據層面是安全的，但在 **資源層面 (Resource Layer)** 仍缺乏有效治理。
若子代理陷入死循環、大量佔用 CPU 或發生記憶體洩漏，將直接威脅 Master 節點的穩定性。

**目標：**
1. **資源配額控制**：限制每個子代理的 CPU 使用率與記憶體峰值。
2. **存活時間 (TTL) 管理**：自動回收超時的懸掛進程。
3. **殭屍進程預防**：確保父進程崩潰時，所有子代理同步終止。

---

## 2. 技術方案評估 (Technical Options)

### 方案 A: Windows Job Objects (原生級控制)
使用 Win32 API 將子進程加入 Job Object，可設定：
- `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`: 父進程關閉時自動殺死子進程。
- `JOB_OBJECT_LIMIT_PROCESS_MEMORY`: 限制單個進程記憶體。
- `JOB_OBJECT_LIMIT_JOB_MEMORY`: 限制整個工作組記憶體。
- **優點**：硬性限制，極低開銷，最為穩定。
- **缺點**：平台相關 (Windows Only)。

### 方案 B: `psutil` 守護線程 (監控級控制)
在 `spawn_manager.py` 中啟動背景監控線程，定期輪詢子代理狀態：
- 定期檢查 `cpu_percent()` 與 `memory_info().rss`。
- 超過閾值時執行 `terminate()`。
- **優點**：跨平台，邏輯靈活（可實作軟限制）。
- **缺點**：有輪詢延遲，且若監控線程失效則無效。

---

## 3. 建議實作策略 (Proposed Strategy)

### Phase 165 波次規劃：
1. **Wave 1 (Windows Job Objects Integration)**:
   - 封裝 `win32_resource.py` 工具類。
   - 修改 `spawn_manager.py`，在 `Popen` 之前/後將 handle 綁定到專屬 Job Object。
2. **Wave 2 (TTL & Heartbeat System)**:
   - 引入 `AA_AGENT_TTL` 環境變數。
   - 實作超時自毀機制。
3. **Wave 3 (Resource Reporting)**:
   - 擴展 `aa-harness status` 與 `orchestrate agents`，顯示各 Agent 的實時資源佔用 (CPU/MEM)。

---

## 4. 預判邊界與風險 (Risks & Boundaries)
- **邊界**：某些大型工具 (如 Vivado/Vitis) 需要較大記憶體，配額需具備角色感知 (Role-aware quota)。
- **風險**：Job Objects 可能與某些防毒軟體或企業安全策略衝突。
- **假設**：目前主要運行環境為 Windows 10/11。

---

## 5. 8 維度檢查 (GSD v2.1)

| 維度 | 說明 |
| :--- | :--- |
| **1. 需求拆解** | 包含 CPU 限制、記憶體限制、TTL 限制、生命週期聯動 |
| **2. 技術選型** | 優先使用 Windows Job Objects (硬限制) + psutil (回報) |
| **3. 系統架構** | 升級 `spawn_manager` 與 `vfs_guard` 的資源監控層 |
| **4. 並行設計** | 使用 `threading.Timer` 處理 TTL，不阻塞主循環 |
| **5. 資安設計建模** | 防止惡意 Prompt 觸發資源耗盡攻擊 (DoS) |
| **6. AI 產品考量** | 提供 "Resource Throttled" 警告，引導用戶調整難度或模型 |
| **7. 錯誤處理** | 資源超限時產生 `ResourceExceededException` 並自動快照狀態 |
| **8. 測試策略** | 撰寫 `test_resource_leak.py` 模擬死循環與大內存分配 |

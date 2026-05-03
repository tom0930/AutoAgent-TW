# Phase 171: Multi-Agent Coordination & AI Omniscient Assistant
## AutoAgent-TW 下一代多代理協作架構設計

**版本**: v1.0 (Discuss Phase)
**日期**: 2026-05-03
**設計者**: Tom (Senior Architect, AI Product Expert, Security Engineer)

---

## 1. 需求拆解與邊界定義

### 1.1 兩大核心需求

**需求 A: Multi-Agent Coordination (多代理並行協作)**
- 多個功能型 Agent 能夠**並行**執行不同子任務
- Agent 間能夠透過**共享匯流排 (Shared Bus)** 感知彼此進度
- 支援 **Supervisor → Worker** 與 **Peer-to-Peer** 兩種協作模式
- 任何 Agent 失敗，不影響其他 Agent（隔離原則）

**需求 B: IDE Omniscient Agent (全能 AI 助手)**
- Antigravity IDE 啟動後自動喚起的**常駐 AI 伴侶 (Persistent AI Companion)**
- 感知 IDE 當前上下文（打開文件、錯誤、游標位置、最近 git 變更）
- 主動推送建議（Proactive Suggestions），不需要用戶主動詢問
- 整合 AutoAgent-TW 所有工作流（`/aa-*` 指令）為自然語言介面

### 1.2 DoD (Definition of Done)
- [ ] 可同時運行 ≥ 3 個 Agent，各自獨立完成子任務
- [ ] Agent 失敗不影響整體任務（99.9% Resilience）
- [ ] IDE 全能助手在 Antigravity 啟動後 < 3 秒完成初始化
- [ ] 全能助手能感知當前文件的 Lint 錯誤並主動提示修復
- [ ] 所有 Agent 間通訊均通過 Phase 170 的 Input Sanitizer

---

## 2. 技術選型與理由

### 2.1 多代理協作框架

| 方案 | 優點 | 缺點 | 推薦度 |
|------|------|------|--------|
| **A: LangGraph 擴展** (現有) | 已有基礎、LangGraph 支援 Human-in-loop | 單一進程、無跨進程隔離 | ⭐⭐⭐⭐ |
| **B: CrewAI Role-based** | 直觀的角色定義、內建任務分配 | 難以整合自定義 MCP | ⭐⭐⭐ |
| **C: 自建 Actor Model** | 完全控制、最佳隔離 | 開發成本高 | ⭐⭐ |
| **D: AutoGen (Microsoft)** | 成熟的多代理框架 | 過重、依賴複雜 | ⭐⭐ |

**結論：選擇 A (LangGraph 擴展) + 自建 Shared Event Bus**
- 理由：Phase 170 的 Streaming Event Bus 可以直接作為 Agent 間通訊的底層
- 每個 Worker Agent 在獨立線程中運行（Thread Isolation），共享同一個 Event Bus

### 2.2 IDE 全能助手架構

| 方案 | 優點 | 缺點 | 推薦度 |
|------|------|------|--------|
| **A: Antigravity Extension API** | 深度整合、感知 IDE 狀態 | 需要 IDE 開放 API | ⭐⭐⭐⭐⭐ |
| **B: LSP (Language Server Protocol) 擴展** | 標準化、跨 IDE | 延遲較高、協議複雜 | ⭐⭐⭐ |
| **C: Side Panel Webview (Electron)** | 豐富 UI、React 支援 | 記憶體佔用高 | ⭐⭐⭐ |

**結論：選擇 A + 搭配 MCP Protocol 橋接 IDE 事件**
- 實現「IDE 事件 → MCP Tool → AutoAgent-TW」的完整感知鏈
- 全能助手通過 MCP 的 `workspace/status` Tool 讀取 IDE 狀態

---

## 3. 系統架構圖

```
┌─────────────────── Antigravity IDE ─────────────────────────────────┐
│                                                                     │
│   ┌───────────────────────────────────────────────────────────┐    │
│   │           AI Omniscient Assistant (Side Panel)            │    │
│   │   - Context Awareness: 文件、錯誤、Git Status             │    │
│   │   - Proactive Suggestions Engine                          │    │
│   │   - Natural Language → /aa-* Workflow Bridge              │    │
│   └────────────────────────┬──────────────────────────────────┘    │
│                            │ MCP Protocol                          │
└────────────────────────────┼───────────────────────────────────────┘
                             │
┌────────────────────────────▼───────────────────────────────────────┐
│                  AutoAgent-TW Core Layer (Phase 171)               │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                  Agent Coordinator Hub                      │  │
│  │         (Phase 170 Streaming Bus as backbone)               │  │
│  │                                                             │  │
│  │  ┌───────────────┐  ┌─────────────────┐  ┌─────────────┐  │  │
│  │  │  Agent Alpha  │  │   Agent Beta    │  │  Agent Gamma│  │  │
│  │  │  (Coder)      │  │   (Tester)      │  │  (Reviewer) │  │  │
│  │  │  Thread-A     │  │   Thread-B      │  │  Thread-C   │  │  │
│  │  └───────┬───────┘  └────────┬────────┘  └──────┬──────┘  │  │
│  │          │                   │                   │         │  │
│  │          └───────────────────▼───────────────────┘         │  │
│  │                    Shared Event Bus                         │  │
│  │              (Phase 170: streaming.py)                      │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                            │                                       │
│  ┌─────────────────────────▼──────────────────────────────────┐   │
│  │             Security & Persistence Layer                    │   │
│  │   Input Sanitizer | Audit Logger | Checkpoint V2           │   │
│  └─────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────┘
```

### 3.1 Agent 角色定義

| Agent 角色 | 職責 | 專屬工具 |
|-----------|------|---------|
| **Coordinator** | 任務分解、分配、結果聚合 | 全局 MCP Router |
| **Coder Agent** | 代碼生成、重構 | `edit_file`, `run_command` |
| **Tester Agent** | 測試執行、回歸分析 | `run_command`, `read_file` |
| **Reviewer Agent** | 代碼審查、資安掃描 | `grep_search`, `Sandbox Evaluator` |
| **Omniscient Agent** | IDE 感知、主動建議 | `workspace/status` MCP, `mempalace_search` |

---

## 4. 並行與效能設計

### 4.1 Agent 線程模型
```python
# 每個 Worker Agent 在獨立線程中運行
# 共享同一個 Event Bus（Thread-safe Queue）
class AgentWorker(threading.Thread):
    def __init__(self, role: AgentRole, task: Task, bus: EventBus):
        super().__init__(daemon=True)
        self.role = role
        self.task = task
        self.bus = bus      # Shared (Thread-safe)
        self.result = None
    
    def run(self):
        # 1. 通知啟動
        self.bus.publish(WorkflowEvent(EventType.AGENT_STARTED, self.role.value))
        try:
            self.result = self._execute(self.task)
            self.bus.publish(WorkflowEvent(EventType.AGENT_COMPLETED, str(self.result)))
        except Exception as e:
            self.bus.publish(WorkflowEvent(EventType.AGENT_FAILED, str(e)))
```

### 4.2 並行任務鏈 (Wave 並行化)
- Wave 1: Coordinator 分解任務 → 並行啟動 N 個 Worker Thread
- Wave 2: Worker 完成後通知 Coordinator → Coordinator 聚合結果
- Wave 3: Reviewer Agent 審核聚合結果 → 產出最終報告

### 4.3 死鎖預防
- Agent 間**禁止直接呼叫**，只能透過 Event Bus 發布事件
- 所有任務有 TTL（預設 5 分鐘），超時自動 Kill 並記錄 Audit Log

---

## 5. 資安設計與威脅建模 (STRIDE)

| 威脅類型 | 攻擊向量 | 防禦措施 |
|---------|---------|---------|
| **Spoofing** | 惡意代理偽裝為高信任 Agent | Agent 身份 Token（每個 Agent 啟動時生成一次性 UUID） |
| **Tampering** | Agent 修改其他 Agent 的輸出 | Event Bus 消息帶 HMAC 簽名（沿用 Phase 170） |
| **Repudiation** | Agent 否認執行了某個操作 | 所有 Agent 操作寫入 Audit Logger（L7） |
| **Information Disclosure** | 低信任 Agent 讀取高信任 Agent 的上下文 | Session 隔離（每個 Agent 獲取獨立的 Context View） |
| **Denial of Service** | 惡意任務讓 Coder Agent 進入無限循環 | 每個 Agent 線程有 TTL + 資源上限（CPU/Memory）|
| **Elevation of Privilege** | Tester Agent 嘗試執行 `rm -rf` | Sandbox Evaluator（L5）強制評估所有命令 |
| **Prompt Injection (AI-特有)** | 透過代碼文件注入惡意指令 | Input Sanitizer（L1）在 Agent 讀取任何文件前先掃描 |

---

## 6. AI 產品相關考量

### 6.1 IDE 全能助手 UX 設計
**核心 UX 原則**：「主動感知，按需介入，永不打擾」

```
[IDLE 狀態]: 靜默，僅在角落顯示小圓圈（綠色=健康，橙色=有建議）
[ACTIVE 狀態]: 彈出側邊欄，顯示「Smart Suggestions」
[CRISIS 狀態]: 強制介入，顯示錯誤診斷與修復方案
```

### 6.2 Proactive Suggestion Engine（主動建議引擎）
**觸發條件**：
1. **文件保存時**: 掃描 Lint 錯誤 → 主動提供修復建議
2. **切換文件時**: 查詢 MemPalace → 提示相關歷史決策
3. **Git Commit 前**: 觸發 Preflight Check → 提示潛在問題
4. **測試失敗時**: 自動啟動 `/aa-fix` 診斷流程

### 6.3 Token 成本控制
- Omniscient Agent 使用**分級掃描**：
  - L0 (Free): 本地規則引擎分析（無 LLM 調用）
  - L1 (Cheap): 快取 + 小型 LLM (Flash)
  - L2 (Premium): 完整 LLM 分析（僅在 CRISIS 狀態觸發）

---

## 7. 錯誤處理、監控與恢復策略

### 7.1 Agent 故障隔離
```python
class AgentCoordinator:
    def run_parallel_agents(self, tasks: List[Task]) -> List[Result]:
        workers = [AgentWorker(task=t, bus=self.bus) for t in tasks]
        [w.start() for w in workers]
        
        results = []
        for w in workers:
            w.join(timeout=300)  # 5min TTL
            if w.is_alive():
                # Agent 超時，記錄 Audit Log 並繼續
                self.audit_logger.log("AGENT_TIMEOUT", w.role.value, "TTL exceeded")
                w.terminate()  # 安全終止
                results.append(FailedResult(reason="Timeout"))
            else:
                results.append(w.result or FailedResult(reason="Crashed"))
        return results
```

### 7.2 Circuit Breaker（熔斷器）
- 若同一 Agent 在 10 分鐘內連續失敗 3 次，觸發 **熔斷**（暫停該類型 Agent）
- 熔斷恢復策略：指數退避（1s → 2s → 4s → ... → 60s max）

---

## 8. 測試策略

### 8.1 Multi-Agent 測試
- **單元測試**: 測試每個 Agent 角色在 Mock 環境下的行為
- **整合測試**: 測試 Coordinator 在 3 個 Agent 並行下的任務分配與聚合
- **壓力測試**: 10 個 Agent 同時運行，驗證 Event Bus 的吞吐量與線程安全
- **資安滲透測試**: 注入惡意 Agent 嘗試越權操作

### 8.2 IDE 全能助手測試
- **模擬 IDE 事件**: Mock `workspace/status` MCP Tool 的回應
- **UX 響應時間測試**: 確保 Suggestion 在文件保存後 < 500ms 出現
- **Token 效率測試**: 驗證 L0 掃描能攔截 90% 的常見 Lint 錯誤

---

## 9. 開放問題 [ASSUMPTION — 需要 Tom 確認]

> [!IMPORTANT]
> 以下 3 個問題會影響實作方向，請確認後再進入 Plan Phase：

1. **[ASSUMPTION A]** 「Antigravity IDE 全能助手」的 UI 目標是：
   - (a) Antigravity 的 **Web Side Panel**（需要 Antigravity Extension API）
   - (b) 一個**獨立的 CLI 浮動視窗**（使用 `rich` Live Display）
   - (c) **兩者都要**（優先 Web Panel，CLI 為降級方案）
   
2. **[ASSUMPTION B]** 多代理的典型使用場景是：
   - (a) 一次性**批量任務**（例如：同時修復 5 個 Bug）
   - (b) **持久化專家代理**（例如：一個常駐的 Tester Agent 持續監控 CI 結果）
   - (c) 兩者都要
   
3. **[ASSUMPTION C]** 是否需要**代理間自然語言溝通**（Agent A 可以問 Agent B 問題）？
   還是代理間只透過**結構化 Event 傳遞結果**即可？

---

## 10. 建議執行波次 (Waves)

> [!NOTE]
> 以下波次基於 Assumption (c)/(a)/(b) 的預設方案，收到確認後調整。

| Wave | 內容 | 預估工時 | 風險 |
|------|------|---------|------|
| Wave 1 | `AgentCoordinator` Hub + `AgentWorker` 線程模型 + Event Bus 整合 | 中 | 低 |
| Wave 2 | Coder/Tester/Reviewer 角色實作 + 並行任務鏈 | 中高 | 中 |
| Wave 3 | IDE Omniscient Agent + MCP `workspace/status` 橋接 | 高 | 中高 |
| Wave 4 | Proactive Suggestion Engine + UX Side Panel UI | 高 | 中 |
| Wave 5 | Circuit Breaker + Agent TTL + 壓力測試 | 中 | 低 |

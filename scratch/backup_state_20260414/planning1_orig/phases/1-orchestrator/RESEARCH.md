# 修改問題加版本version: v1.9.0
# Phase 1: 子代理系統與平行任務調度 - 領域研究 (RESEARCH)

## 1. 系統現況分析
目前 AutoAgent-TW 的流程控制主要依賴：
1. `scripts/aa_chain_orchestrator.py`: 僅支援線性指令鏈 (`&&`, `||`, `|`)，無法處理真正的平行多線程與上下文合併。
2. `scripts/scheduler_daemon.py`: 負責排程管理 (Cron/Interval)，使用 `apscheduler` 進行非同步任務發佈。

現有架構無法輕易滿足 "Coordinator" 進行任務動態拆解，再平行發派 "SubagentSpawnManager" 的需求。這需要一個能呼叫外部 Claude API 的子代理邏輯。

## 2. 核心架構設計 (Spawn Manager & Coordinator)
- **SubagentSpawnManager**:
  - 角色：負責建立、監控、回收獨立的背景 AI 任務 (子程序形式)。
  - 溝通機制：可透過 JSON 寫入共享目錄 `.agent-state/subagents/` 或使用 stdout pipe 回傳結果。
  - 需要防呆機制：設定 Timeout 限制，並監控預算 Tokens 使用量。

- **Coordinator**:
  - 角色：如同樂團指揮，將高階目標 `High-Level Goal` 交由 LLM 拆解為 `[Research, Implement, Verify]` 步驟。
  - 執行模式：同步等待 (blocking wait) 彙整多個 Research 子代理結果，再進行規劃，然後再次發動 Implement 子代理。

- **指令介面**:
  - `/aa-orchestrate`：將作為 CLI 入口點，接受用戶目標，實例化 Coordinator 開始運作。

## 3. 已知技術挑戰與陷阱 (Pitfalls)
1. **依賴管理**: 需引入 `anthropic` SDK 以實作子代理自身的大型語言模型呼叫能力。這代表新架構需配置 `ANTHROPIC_API_KEY` 環境變數。
2. **Race Condition**: 若平行子代理同時嘗試修改同一份程式碼，可能會遭遇 Git 或檔案鎖的衝突。
   - *解法*: 在 Wave 內，不同 Implementer 子代理**必須負責互不重疊的檔案**。Coordinator 拆解任務時需明確做好區域隔離。
3. **錯誤處理 (Resilience)**: 如果某個子代理失敗 (逾時或 Token 耗盡)，Coordinator 必須具備重試或備援機制。

## 4. 實施方案評估
- 方案 A (純 Shell 子進程): `SpawnManager` 使用 `subprocess.Popen` 直接呼叫獨立的 python agent code。優點是環境隔離，缺點是通訊較無效率。
- 方案 B (Asyncio 平行協程): `SpawnManager` 使用標準 Python `asyncio` 執行 LLM API 呼叫。優點是資源極省、通訊共用記憶體。
  - **推薦方案**: 方案 B (Asyncio)，因為子代本質上是 I/O-bound (等待 Claude API 回應)，無需開啟大量 Python Process 浪費記憶體。

## debug printf問題
- `run_step` 或 Coordinator 內部應加入完整的 debug logging，顯示每個子代理的 ID、消耗 Token 與當前狀態，以便除錯。

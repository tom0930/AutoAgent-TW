# Phase 124 Research: Sub-Agent Orchestration & Real-time Sync

## 1. 實施方案分析 (Implementation Analysis)
### 1.1 LangGraph 編排邏輯
- 採用 **Supervisor 節點** 負責任務拆解與依賴判斷。
- **Worker 節點** 封裝 `subprocess.Popen` 呼叫，實現「非阻塞、高度隔離」的子任務執行。
- `StateGraph` 的狀態需包含 `subtask_id`, `assigned_to`, `status`, `result` 等字段。

### 1.2 Dashboard 即時推送機制
- 現有 `status_updater.py` 已支援掃描 `.agent-state/subagents/*.json`。
- **優化方案**: 子代理在啟動時自動分配 UUID，並持續更新其專屬的 JSON 狀態檔。
- **頻率控制**: 限制子代理寫入頻率（如每 2 秒一次），避免磁碟 I/O 競爭導致 Dashboard 讀取掛掉。

## 2. 依賴檢查 (Dependency Check)
- `langgraph`: OK (v0.1.0+)
- `portalocker`: OK (用於確保 `.agent-state/status_state.json` 寫入時的原子性，避免 Windows 下的併發衝突)
- `psutil`: OK (用於監控子進程資源佔用)

## 3. 已識別的陷阱 (Identified Pitfalls)
- **JSON 競爭**: 雖然子代理寫入獨立文件，但 `status_updater` 聚合時若讀取到正在寫入的一半的文件會報錯。須強化 `status_updater` 的異常處理。
- **Zombie Processes**: 若主控 Daemon 崩潰，子代理可能會變成孤兒進程。需在 `spawn_manager` 加入 `atexit` 清理機制。
- **Token 暴走**: 多個 Agent 平行執行時，若無全局總控，可能瞬間耗盡預算。

## 4. 參考資源
- LangGraph Docs: Multi-agent interaction patterns.
- Python `subprocess` documentation for `STARTUPINFO` (Windows specific isolation).

# Phase 164 Research: Subagent Context Isolation (Axis 2)

## 1. 實施方案分析 (Implementation Analysis)
### A. 專家角色映射 (Persona Mapping)
- **來源**: `awesome-claude-code-subagents` (VoltAgent)。
- **核心角色**: `architect-reviewer`, `security-auditor`, `code-reviewer`, `performance-engineer`。
- **儲存**: `.agents/personas/{role}.md`。

### B. 角色感知過濾 (Role-aware Pruning)
- **機制**: 透過 `RTK` (Rust Token Killer) 的 Hook，根據子代理的 `AA_SUBAGENT_ROLE` 環境變數，動態過濾 Token。
- **規則範例**:
  - `cpp-expert`: 只允許 `.cpp`, `.h`, `.hpp`, `.cu`, `.tcl`。過濾 `.py`, `.js`, `.md` (除了 README)。
  - `security-auditor`: 允許所有代碼，但過濾掉具體的數據內容 (Data Sanitization)，保留邏輯結構。

### C. 邏輯 VFS 沙盒 (Logical VFS Sandbox)
- **攔截點**: 在 `src/core/orchestration/vfs_guard.py` 實作一組攔截器。
- **邏輯**: 子代理嘗試調用 `read_file` 時，Hook 會檢查其 `subagents.json` 的路徑白名單。

## 2. 依賴檢查 (Dependency Check)
- **RTK**: 需確保 `bin/rtk.exe` 支援傳遞 `--role` 參數。
- **SpawnManager**: 現有的 `AgentProcess` 需擴展 `role` 欄位。

## 3. 已識別的陷阱 (Identified Pitfalls)
- **[PITFALL] 過度隔離**: 如果隔離太嚴格，子代理可能因為缺乏必要的跨模組 Context 而無法解決問題。
  - **對策**: 提供 `global_context_files` 配置，包含 `PROJECT.md` 與 `ARCHITECTURE.md`，這些文件對所有角色可見。
- **[PITFALL] Token 預熱延遲**: 啟動前裁剪 Context 會增加幾百毫秒的延遲。
  - **對策**: 使用非同步裁剪。

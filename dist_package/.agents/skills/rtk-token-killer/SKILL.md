---
name: rtk-token-killer
description: Use this skill for ALL terminal/tool_use commands. Auto-apply RTK Global Hook with dynamic compression levels. Optimized for FPGA (Vivado, Vitis), MFC C++, large compilation logs.
---

# RTK Token Killer Skill v0.4.3 (AutoAgent-TW)

**Goal**  
在極致 token 壓縮（60-95%）的同時，透過動態策略確保 Builder/QA/Guardian 都能獲得適當資訊量，特別適合 FPGA / MFC 大型專案。

**Dynamic Context Strategy**
- **Builder Phase**: `compact` 模式 -> 只保留 Error + Critical Warning + Summary。
- **QA Phase**: `summary-only` 模式 -> 失敗時自動 `--raw` 取得完整 traceback。
- **Guardian Phase**: `verbose` 模式 -> 完整 log + side-effect 記錄。

**Zero-Token Transparency**
- 每次指令執行前後，會靜默更新 `status-notifier`。
- 顯示當前 Agent 的「執行目地」與「Token 節省率」。

**Instructions**
1. 確保已執行 `rtk init -g --agent antigravity --hook-only`。
2. 偵測當前 Agent 階段（從 .planning 或 workflow context）。
3. 自動在指令後附加適當 flag（--compact / --summary / --raw）。
4. 每次執行後呼叫 `rtk gain --json` 並推送到 status-notifier。

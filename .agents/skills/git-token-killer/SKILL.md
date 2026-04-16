---
name: git-token-killer
description: 強制所有 Git 操作走 RTK 壓縮 + GitKraken MCP 混合模式。針對大型 FPGA/MFC 專案優化 diff、log、status，目標單次 Git 操作省 75-93% token。
trigger: any git command, GitKraken MCP tool use (git_log_or_diff, etc.)
---

# Git Token Killer Skill v1.0 (Phase 143)

**Goal**  
結合 GitKraken MCP 的精準查詢能力 + RTK 的極致壓縮，徹底解決 diff 過大問題，同時保留 QA/Guardian 所需精確度。

**Hybrid 運作模式（核心）**
1. 日常操作（status, log, diff, show）→ 強制走 RTK Proxy 壓縮
2. 需要深度查詢（blame, specific commit, PR）→ 先呼叫 GitKraken MCP，再套 RTK 壓縮 output
3. 自動根據 Phase 調整壓縮強度

**Dynamic Strategy**
- **Builder**: --compact （只留 summary + changed files）
- **QA**: --summary （失敗時自動 --raw）
- **Guardian**: --verbose （保留完整 patch 但壓縮 noise）

**Instructions for AutoAgent-TW**
1. 偵測到 git 相關 tool_use 或 GitKraken MCP call 時，自動改寫為 `rtk git ...`
2. 優先使用以下高效指令：
   - `rtk git status --short`
   - `rtk git log --oneline -10`
   - `rtk git diff --stat` 或 `rtk git diff --compact`
3. 若 LLM 判斷資訊不足 → 自動 fallback `--raw`
4. 每次執行後呼叫 `rtk gain --json` 並推送到 status-notifier

**GitKraken MCP 混合規則**
- 只在需要精準歷史時使用 GitKraken/git_log_or_diff
- 呼叫後必須立即套 RTK 壓縮（wrapper 已處理）
- 禁止直接呼叫 full diff without --stat

**Fallback**
指令加上 `--raw` 即可取得完整原始輸出。

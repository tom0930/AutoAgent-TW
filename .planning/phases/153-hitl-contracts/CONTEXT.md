# Phase 153: Human-in-the-loop Verification Contracts

## 1. 目標 (Goals)
實作工業級的執行合約機制，確保所有具備副作用（Side Effects）的操作皆需經過使用者數位確認。

## 2. 核心架構 (Core Architecture)
- **Trigger**: `mcp-router` 攔截器。
- **Contract Engine**: `src/core/contracts/engine.py`負責生成 Risk Analysis 與計劃摘要。
- **State Store**: `.agent-state/pending_contracts/`。
- **Verification**: 雙重校驗 (Action Hash + Session ID)。

## 3. 高風險工具定義 (Risk Policy)
- `write_to_file` (若變更行數 > 50%)
- `git_push`
- `run_command` (檢索關鍵字: rm, del, format, sudo, systemctl)
- `mcp_GitKraken_git_push`

## 4. 變更流程
1. `Sub-Agent` 發出 `tool_use`。
2. `Router` 判定為 `High Risk`。
3. `ContractEngine` 生成 `CONTRACT.md` 並計算 Hash。
4. 暫停執行，回傳 `AWAITING_APPROVAL` 給使用者。
5. 使用者確認後，帶入簽名繼續執行。

## 5. 資安防護
- 實作防 AI 二次篡改機制 (Seal the Contract)。
- 建立操作備份 Checkpoint。

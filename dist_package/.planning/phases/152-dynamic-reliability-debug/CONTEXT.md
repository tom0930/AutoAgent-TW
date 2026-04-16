# Phase 152: Smart Debug Orchestration & Reliability Testing

## 1. 目標 (Objective)
提升 `/aa-fw-debug` 的智慧化程度，使其具備「自適應任務生成」與「可靠性驗證（多次測試）」能力。確保 AI 不只是修好 Code，還能確保修得「穩」。

## 2. 核心變更與功能 (Core Changes)

### A. 動態任務清單 (Dynamic Tasking)
- **初始規劃階段**：Agent 會解析 `/aa-fw-debug "指令"`，並在 `tests/fw_debug_task.md` 填寫具體的行為指標（例如：監控 DDR 電壓、檢查 AXI 仲裁）。
- **進度追蹤**：Agent 將會根據 `uart_bridge` 傳回的日誌，自主決定是否勾選子項目。

### B. 可靠性循環 (Reliability Loop)
- **Iteration Count**：新增 `flash_config.json` 中的 `verification_threshold` 參數。
- **Pass 條件**：必須連續成功 $N$ 次 (Default=1, 可動態調整)。
- **Fail Pattern 阻斷**：
    - 若日誌匹配到 `[FAIL]`, `[ERROR]`, `HardFault`, `Deadlock` 等預設關鍵字。
    - 立即標記測試失敗，歸零 Pass Counter。

## 3. 系統狀態管理 (State)
存儲於 `.agent-state/fw_debug_session.json`：
```json
{
  "current_phase": "VERIFYING",
  "consecutive_passes": 3,
  "required_passes": 5,
  "fail_patterns_detected": [],
  "current_task_list": "tests/fw_debug_task.md"
}
```

## 4. 資安與冗餘設計 (Safety)
- **Abort Chain**：若在驗證過程中發現 `Smoke Detect` 或硬體熔斷關鍵字，立即終止所有燒錄操作，並提示人類接手。
- **Context Preservation**：每次 Fail 的日誌都會被截圖/存檔至 `logs/{timestamp}_fail.log`，供事後分析。

## 5. 決策 (Decisions)
- 使用 **Judge Agent** 作為決策核心，由它判斷日誌內容是否符合結案標準。
- 支持 **「人類介入選項 (Human-in-the-loop)」**：AI 可以在 Checklist 最後一項提問：「已過 5 次測試，是否需要額外測 10 次或直接結案？」。

# Workflow: AA FW Debug Engine (Master Loop)

## 🎯 任務目標 (Master Goal)
啟動自動化閉環除錯系統，針對用戶輸入的「問題描述」或「修改計畫」進行代碼修正、燒錄驗證與結果審計。

## 🛠 啟動指令格式 (Command Syntax)
`/aa-fw-debug "問題描述或修正計畫"`

## 🔄 核心邏輯 (Cycle Logic)

### Step 1: 任務初始化 (Initialization)
- **Action**: 讀取用戶輸入的 Goal，寫入 `_agent-state/fw_debug_session.json`。
- **Action**: 重置 `tests/fw_debug_task.md` 為初始狀態。
- **Action**: 增加 `attempt_count`。如果超過 `retry_limit` (5)，進入「手動模式模式」並暫停。

### Step 2: 執行者修復 (Worker Phase)
- **Call**: `/aa-plan` -> 執行 `_agents/workflows/worker_agent.md`。
- **Checklist**: 更新 `[x] [Fix]` 當編譯與 `pre_flash_verify` 通過後。

### Step 2.5: 驗證合約審核 (Contract Review)
- **Action**: 讀取 Worker 產出的 Checkpoints 並渲染為選項清單。
- **Interactive**: 提供正向 (Success) 與 負向 (Early Abort) 的勾選框。
- **Pause**: 必須等待用戶回覆「Continue」或修改條。

### Step 3: 指令手動驗收 (Manual Flash Handoff)
- **Action**: 輸出燒錄指令：`python scripts/flash.py`。
- **Pause**: 等待用戶執行完畢後按下「Continue」。


### Step 4: 評審者驗收 (Judge Phase)
- **Call**: `/aa-qa` -> 執行 `_agents/workflows/judge_agent.md`。
- **Checklist**: 更新 `[x] [Verify]`。
- **Judgment**: 
    - 如果 Judge 回傳 `PASS` ➔ 結案並產出 `./walkthrough.md`。
    - 如果 Judge 回傳 `FAIL` ➔ 將回饋寫入 `state.json` 並**遞迴觸發**下一輪 `/aa-fw-debug`。

---

## 📢 當前進度 (Current Status)
目前的偵測進度與 Checklist 紀錄於：[fw_debug_task.md](file:///z:/autoagent-TW/tests/fw_debug_task.md)

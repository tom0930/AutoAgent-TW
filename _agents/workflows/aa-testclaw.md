---
description: TestClaw Autonomous Agent / TestClaw 自主代理模式。
---

# AutoAgent-TW aa-testclaw Workflow

## 觸發條件 (Trigger)
- 使用者輸入 `/aa-testclaw [目標]`。

// turbo-all

## 核心理念
將 AutoAgent-TW 從「線性流水線」升級為「自主代理循環」(Agent Loop)。具備自主規劃、動態工具調用、錯誤恢復與長期記憶。

## 執行步驟：代理循環 (Agent Loop)

### Step 1: 初始化與目標分解 (Initialize & Decompose)
1. 讀取 `.planning/PROJECT.md`。
2. 將使用者目標分解為任務樹 (Task Tree)，儲存於 `.testclaw/plan.json`。
3. 初始化記憶系統 `.testclaw/memory/`。

### Step 2: 核心循環 (The Loop)
執行以下循環直到目標達成或達到最大迭代次數 (預設 50)：

#### 2a. 觀察 (Observe)
- 讀取當前環境：檔案、測試結果、Git 狀態、終端輸出。
- 讀取最近的記憶片段 (Recent Episodes)。

#### 2b. 思考與推理 (Think)
- LLM 分析：目前進度如何？遇到了什麼障礙？
- 評估：是否陷入循環？是否需要調整計劃？
- **產出推理日誌**：記錄於 `.testclaw/thoughts.log`。

#### 2c. 行動決策 (Decide)
- 根據思考結果，從工具箱 (Toolbox) 選擇最合適的工具：
  - `read_file`, `write_file`, `list_dir`
  - `run_command`, `run_tests`
  - `web_search`, `browse_url` (用於搜尋解決方案)
  - `git_status`, `git_commit`, `git_rollback`
  - `ask_human` (僅在必要時)

#### 2d. 執行 (Act)
- 在安全沙箱環境中執行該行動。
- 捕捉輸出、錯誤代碼與影響範圍。

#### 2e. 反思與記憶更新 (Reflect)
- 評估行動結果。
- 儲存為「經驗片段」(Episode) 存入 `.testclaw/memory/episodes.json`。
- 如果失敗，嘗試從記憶中回憶 (Recall) 類似錯誤的解法。

### Step 3: 錯誤恢復 (Recovery)
若循環檢測到進度停滯或多次失敗，啟動恢復策略：
1. **策略 A (Web Search)**: 搜尋最新的技術文件或 StackOverflow 解法。
2. **策略 B (Rollback)**: 使用 Git 回退到上一個穩定的 Commit。
3. **策略 C (Alternative)**: 重新分解目標，嘗試另一條實現路徑。
4. **策略 D (Human)**: 彈出視窗請使用者介入。

### Step 4: 結案與交貨 (Ship)
1. 目標達成後，產生總結報告。
2. 更新 `version_list.md`。
3. 自動執行 `/aa-ship` 進行最終檢查點提交。

## 限制與約束
- **Iteration Limit**: 50 輪循環。
- **Budget Control**: 監控 Token 消耗與外部 API 成本。
- **Sandbox**: 所有檔案修改必須符合路徑白名單。

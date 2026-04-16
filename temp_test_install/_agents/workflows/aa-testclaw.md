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

### Step 1: 初始化
1. 讀取專案狀態並建立 `.testclaw/` 空間。

### Step 2: 核心循環 (Observe-Think-Decide-Act-Reflect)
1. **Observe**: 讀取檔案、測試結果與 Git 狀態。
2. **Think**: LLM 分析現狀，評估進度。
3. **Act**: 調用搜尋、寫碼、執行或 Git 等工具。
4. **Reflect**: 更新記憶片段，分析是否達成目標或陷入循環。

### Step 3: 多層級恢復 (Recovery)
若失敗，依序嘗試：網搜、回退、更換路徑或詢問人類。

### Step 4: 結案
目標達成後，更新版本日誌並出貨。

## 限制
- **Limit**: 50 輪迭代。
- **Memory**: 定期清理過期片段。

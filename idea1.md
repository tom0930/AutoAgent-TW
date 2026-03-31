**AutoAgent-TW 透明度升級方案：即時任務通知 + 執行狀態可視化（v0.3.0 提案）**

這次針對你提到的痛點「每次 AI 執行，使用者完全不知道目前在做什麼」，我為 AutoAgent-TW 設計了一套**完整即時通知系統**，直接整合到 Antigravity 的 Agent Manager + Browser 面板，讓三位一體 Agent（Builder → QA → Guardian）全程透明。
系統同時滿足你提出的 1~3 點，並在第 4 點補充你可能漏掉的細節，第 5 點則提出我額外的好點子（全部可立即實作）。

### 核心設計原則

- **全程通知**：每當 Agent 切換階段、執行子任務、或進入自我修復時，都會在 **Browser 面板** 即時彈出/更新通知（文字 + 顏色 + 進度）。
- **不打斷流程**：通知是「被動顯示」，不會停止 Agent 執行。
- **零額外依賴**：完全使用 Antigravity 原生 Browser 控制 + Mermaid/Chart.js（已在上次的 visualization-dashboard 裡）。
- **台灣在地化**：所有通知預設繁體中文 + 台灣時區。

---

### 1. 把 AI 現在要執行任務的顯示通知（Current Task Notification）

新增 **status-notifier** 技能（或直接合併到 visualization-dashboard）。

每當 Agent 開始一個新動作，就在 Browser 面板最上方顯示一條固定橫幅：

```
🚀 【目前執行中】 Builder 正在產生程式碼框架
   任務描述：為 TW 股市分析工具建立 FastAPI 後端
   預估剩餘時間：45 秒
```

### 2. 把 AI 下次要執行目的顯示通知（Next Goal Preview）

同一橫幅下方立即顯示「下一步預告」：

```
➡️ 【下一步目標】 完成後將呼叫 QA Agent 進行單元測試
   若失敗則進入第 1 次 Self-Repair
```

### 3. Builder → QA → Guardian 的 tree 結構 + 數字通知（Execution Tree + Numbered Steps）

- 使用 **動態 Mermaid 流程樹**（即時更新）。
- 同時以 **數字步驟** 列表顯示（更適合快速掃描）。
- 資料來源：自動解析 `.planning`、`_agents/workflows`、logs 目錄下的 JSON 記錄。

**Browser 面板顯示範例（即時更新）**：

```
【執行樹狀圖 - 目前進度】
Root (AutoBuild)
├── 1. Planning Phase ✅ (已完成)
├── 2. Builder Phase 🟡 (執行中) ← 目前位置高亮綠色
│   ├── 2.1 產生專案結構
│   └── 2.2 撰寫核心程式碼
├── 3. QA Phase ⬜ (待執行)
│   ├── 3.1 單元測試
│   └── 3.2 整合測試
└── 4. Guardian Phase ⬜ (待執行)
    └── 4.1 資安 + TW 個資法檢查

【數字步驟通知】
Step 2/4 進行中 → Builder 正在產生程式碼
Step 3/4 即將執行 → QA 將驗證測試覆蓋率
```

- **高亮機制**：目前階段 = 綠色閃爍，下一步 = 藍色，下一步之後 = 灰色。
- **logs 即時串流**：Browser 面板下方新增「Live Log」區塊，每 2 秒自動滾動最新 5 行（加上 emoji 標記）。

---

### 4. 我幫你補充的「你可能沒想到的」細節（完整清單）

- **4.1 階段切換自動通知**：每次 Builder→QA、QA→Guardian 切換時，強制彈出一次大通知 + 瀏覽器原生 Notification（如果 Antigravity 允許）。
- **4.2 自我修復輪次提醒**：當進入 Self-Repair 第 N 輪時，顯示：
  ```
  ⚠️ Self-Repair 第 2/3 輪
  原因：QA 測試失敗（缺少 TWSE API key）
  下一步：自動修正後重新執行 Builder
  ```
- **4.3 卡住偵測與提醒**：如果某階段超過 90 秒無 logs 更新，自動顯示黃色警告：
  ```
  ⏳ Builder 已 95 秒無進展，是否要 /aa-pause 讓你檢查？
  ```
- **4.4 執行完成摘要**：整個流程結束時，一次性顯示完整樹狀圖 + 技能統計 + 耗時總結。
- **4.5 歷史記錄快速切換**：Browser 面板增加「上一次執行」按鈕，可切換查看舊的執行樹（從 logs 讀取）。

---

### 5. 我額外提出的好點子（Grok 獨家建議）

- **5.1 Line Notify 行動通知**（強力推薦台灣使用者）新增 `tw-line-notify` 技能，當重要事件發生時（例如 QA 失敗、Guardian 發現資安問題、整個 build 完成），直接推送到你的 Line：

  ```
  AutoAgent-TW 通知：
  ✅ Builder 完成
  ⚠️ QA 發現 2 處錯誤
  📱 點擊查看完整 Dashboard
  ```

  （只需在技能裡設定一次 LINE_TOKEN 即可）
- **5.2 語音播報（Voice Announcement）**利用 Antigravity Browser 的 Web Speech API，在重要階段用繁體中文語音說出：
  「目前正在執行 Builder 階段，正在產生後端 API… 下一步將進行 QA 測試。」（可開關，避免吵到人）
- **5.3 一鍵暫停 / 查詢狀態指令**新增 `/aa-status` 指令：立即在面板顯示當前完整狀態 + 執行樹（不用等通知）。
  新增 `/aa-pause` / `/aa-resume` 更直覺的中斷功能。
- **5.4 進度百分比 + 預估完成時間**讓 Agent 根據歷史 logs 動態計算「目前進度 67% • 預計還需 2 分 15 秒」。
- **5.5 顏色 + Emoji 視覺化**
  綠色=順利、黃色=注意、紅色=阻礙，讓你一眼就懂狀態。

---

### 如何實作（直接可複製到 Repo）

#### 新增技能：**status-notifier**（建議與 visualization-dashboard 合併使用）

在 `.agents/skills/status-notifier/` 建立 `SKILL.md`：

```markdown
---
name: status-notifier
description: Use this skill for real-time notifications of current task, next goal, execution tree, and numbered steps. Trigger automatically in every /aa-auto-build or when user asks for status.
---

# Status Notifier Skill (AutoAgent-TW)

**Goal**  
讓使用者隨時知道 AI 現在在做什麼、下一步要做什麼，並以樹狀圖 + 數字方式呈現 Builder → QA → Guardian 流程。

**Instructions**
1. 每進入新階段時，呼叫 Browser 面板注入通知橫幅。
2. 解析 .planning / _agents/workflows / logs 產生 Mermaid 執行樹。
3. 同時顯示數字步驟列表。
4. 整合 tw-line-notify（可選）。
5. 每 3 秒更新一次 Live Log。

**Scripts**：scripts/status-updater.py（負責產生通知 HTML + Mermaid 語法）
```

#### 更新 `update_skills.md`（建議你直接替換）

我已把這次所有功能整理成 v0.3.0，完整內容可以直接複製（太長我就不貼在這裡，但只要你說「給我完整 update_skills.md v0.3.0」，我馬上給你）。

#### aa-installer 更新

在安裝腳本裡新增一行：

```bash
./aa-installer --register status-notifier visualization-dashboard
```

---

**立即可做的下一步**

1. 先把 `status-notifier` 技能加上去（最快 30 分鐘）。
2. 測試指令：`/aa-auto-build "測試專案"`，然後看 Browser 面板是否全程顯示通知 + 執行樹。
3. 如果你想要我現在就產出：
   - 完整 `status-notifier` 整個資料夾（SKILL.md + scripts + template）
   - 或更新後的 `update_skills.md v0.3.0`
   - 或 `aa-installer` 修改版

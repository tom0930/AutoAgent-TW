---
description: Initialize New Project / 初始化新專案。
---

# AutoAgent-TW New Project Workflow

## Phase 0: 初始化

### Step 1: 目錄結構與初始化
// turbo
1. 檢查是否已存在 `.planning/PROJECT.md`。若已存在且有內容，則跳至 `/aa-progress`。
2. 檢查 git 是否初始化，若無，執行：
```bash
git init
```
3. 建立基礎目錄結構：
```bash
mkdir -p .planning/research .planning/phases .agent-state
```

### Step 1.5: Context Guard — 自動生成 .geminiignore
// turbo
1. 執行 Context Guard 前置掃描：
```bash
python scripts/context_guard.py .
```
2. 若 `.geminiignore` 不存在，`context_guard.py` 會自動生成預設版本。
3. 若已存在，則驗證覆蓋率並回報缺漏。
4. 此步驟確保 Antigravity 不會因索引二進位檔而觸發 Max Token Limit Error。

### Step 2: 深度訪談 (Deep Questioning)
**如果是 `--auto` 模式：**
- 自動讀取輸入文件（如 PR 或 Issue 詳情）。
- 使用推薦的預設配置。

**如果是交互模式：**
1. 詢問使用者：專案主要是要做什麼？
2. 明確核心技術棧、Granularity (粒度)、模式 (YOLO vs Interactive)。
3. 確認完成後產出 PROJECT.md。

### Step 3: 建立 PROJECT.md
1. 將訪談結果寫入 `.planning/PROJECT.md`。
2. 包含：專案背景、核心價值、技術目標、已定義的變量與路徑。
3. Commit：
```bash
git add .planning/PROJECT.md
git commit -m "docs: initialize project context"
```

### Step 4: 工作流細項設定
1. 寫入 `.planning/config.json` 設定開發偏好 (YOLO/Granularity 等)。
2. Commit：
```bash
git add .planning/config.json
git commit -m "chore: add project initial config"
```

### Step 5: 領域研究 (Research)
1. 建立 `.planning/research/`。
2. 產出 `STACK.md` (技術棧)、`FEATURES.md` (功能對照)、`ARCHITECTURE.md` (架構建議)。
3. 匯總成 `SUMMARY.md`。
4. Commit 研究文檔。

### Step 6: 定義具體需求 (Requirements)
1. 產出 `.planning/REQUIREMENTS.md`。
2. 列出 v1/v2 版本的具體需求 ID (如 AUTH-01)。
3. 確保需求與專案目標對齊。
4. Commit 需求文件。

### Step 7: 建立發展路線圖 (Roadmap)
1. 產出 `.planning/ROADMAP.md`，將需求拆解為多個 Phases。
2. 產出 `.planning/STATE.md` 初始化當前狀態。
3. 在 `.agent-state/current-phase` 寫入 `1`。
4. Commit 路線圖與狀態：
```bash
git add .planning/ROADMAP.md .planning/STATE.md .agent-state/
git commit -m "docs: create project roadmap"
```

### Step 8: 完成
1. 提示專案已初始化。
2. 建議執行 `/aa-discuss 1` 或 `/aa-plan 1` 開始對應的第一階段開發。

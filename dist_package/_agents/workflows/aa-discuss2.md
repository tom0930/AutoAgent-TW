---
description: Stage1Discuss
---

# AutoAgent-TW: Discuss Workflow (v2.1)

## Input
- Phase number: N (from $ARGUMENTS)

// turbo-all

## Steps

### Step 0: 歷史上下文檢索 (Memory Retrieval)
// turbo
1. 執行 `mempalace search "Phase {{N}} 相關設計與過往決策"`。
   > [!IMPORTANT]
   > 搜尋將自動鎖定本地 `mempalace.yaml` 定義的 Wing，確保不會檢索到其他無關專案的私密記憶。
2. 參考 `mempalace` 提供的歷史 Wings/Rooms 資訊，避免重複錯誤或遺漏關鍵決策。

### Step 1: 匯入當前上下文與意圖挖掘
1. 讀取核心計畫文件：
   - `.planning/PROJECT.md`
   - `.planning/REQUIREMENTS.md`
   - `.planning/ROADMAP.md`
2. 掃描現有代碼結構，確認技術債與依賴關係。

### Step 2: 邊界定義與約束確認
1. 明確 Phase N 的 **DoD (Definition of Done)**。
2. 定義非功能性需求：性能、擴展性、跨平台限制。

### Step 3: 架構選型與 Trade-off 討論
1. 提出至少兩種技術方案論證。
2. 討論並發模型、數據持久化策略及第三方模組整合。

### Step 4: 資安威脅建模 (STRIDE)
1. 針對當前 Phase 執行 STRIDE 分析。
2. 識別攻擊向量並定義防禦策略。

### Step 5: 編排策略與自動化模式 (Orchestration)
1. 判斷是否可用 Wave 並行化。
2. 如果是 `--auto` 模式：自動選用建議配置。

### Step 6: 產出 CONTEXT.md 與 Commit
1. 建立目錄：`.planning/phases/{N}-phase-name/`。
2. 寫入 `CONTEXT.md` (目標、決策、架構、資安)。
3. Commit 變更：
```bash
git add .planning/
git commit -m "docs: phase ${N} architectural context - v2.1 (stable)"
```

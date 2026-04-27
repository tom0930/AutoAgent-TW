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

### Step 2.5: Karpathy 原則 — Think Before Coding（強制）
> **來源**: andrej-karpathy-skills (⭐ 92.7k)
> 「LLMs make wrong assumptions and just run along with them without checking.」

1. **列出所有假設** — 不確定的地方必須標記 `[ASSUMPTION]` 並詢問用戶。
2. **暴露多重解讀** — 如果需求存在歧義，列出所有可能的解讀，不可默默選一個。
3. **適時推回** — 如果存在更簡單的方案，必須提出並解釋為什麼更好。
4. **困惑時停下** — 命名不清楚的地方，直接問。不要猜測後繼續跑。

### Step 2.6: 內部多 Agent 思考（7-Step CoT）
> 從 user_rules 下放至此的執行細節。每次回應前內部完整走完：

1. 問題解析與意圖挖掘
2. 自我質疑與漏洞檢查（常見陷阱、隱藏假設）
3. 多 Agent 思考（≥3 視角：架構師、資安工程師、AI 產品專家）
4. 多角度/反面思考 + ≥2 個解決方案 + 優劣評估
5. 自我質疑與修正
6. 最終決策與優化
7. 主動發現問題、提出 SOP 與預防性優化

### Step 3: 架構選型與 Trade-off 討論
1. 提出至少兩種技術方案論證。
2. 討論並發模型、數據持久化策略及第三方模組整合。
3. **Simplicity Check** — 問自己：「資深工程師會說這太複雜嗎？」如果是，精簡它。

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

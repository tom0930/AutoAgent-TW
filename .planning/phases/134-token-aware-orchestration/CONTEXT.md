# Phase 134: Token-Aware Execution & Sub-task Splitting (Context)

## 🎯 核心目標 (Core Objective)
解決長線條任務 (Long-horizon tasks) 中遇到的 Token 爆炸與上下文崩潰 (Context Rot) 問題。將巨型計畫拆分為原子化子任務，並導入執行前 Token 複雜度評估機制。

## 🧠 設計決策 (Design Decisions)

### 1. 拒絕巨型 PLAN 檔案 (Atomic Sub-tasks)
*   **現狀痛點**：過去的 Phase 常常在一個 `PLAN.md` 內包含 20~50 個步驟。執行到後半段時，AI 無法記住前面的細節，且每次溝通都會燒掉大量 Token。
*   **新架構**：將一個 Phase 拆解為 `134.1`、`134.2` 等 Micro-Phases 或 Tasks。
    *   廢棄一次性寫好所有細節的巨型 `PLAN.md`。
    *   每個 Sub-task 只讀取必要的最小上下文（例如僅載入具體要改的 2 個檔案），完成後生成極短的 `.summary` 存檔。

### 2. 執行前的「複雜度與 Token 預判」(Pre-flight Token Check)
*   **現狀痛點**：現在的 `running_temp` 僅是用來記錄「我跑到哪一步了」，並沒有「思考這一步該怎麼跑才划算」。
*   **新架構**：在下達 `/aa-execute` 時，Agent 必須先進行**動態分流 (Dynamic Routing)**：
    1.  **簡單任務 (Low Token / Clear Path)**：走傳統 Pipeline 流水線（最省成本）。
    2.  **複雜任務或環境依賴 (High Token / Unknowns)**：若是遇到 API 授權、環境部署、未知的外部庫，主動將執行模式切換為 **`/aa-orchestrate`** 代理模式。

### 3. 與 `running_temp` 的功能區隔
*   **`running_temp` 為「事後記帳理論」**：記錄已發生的步驟與 Token 消耗，用於斷點續傳。
*   **本機制為「事前報價理論」**：在 LLM 發送請求前，利用「啟發式算法 (Heuristic)」根據讀取檔案的字元數 (Char Count / 4) 與步驟複雜度預估風險。這兩者互為表裡，Scorer 預測預算，running_temp 監控執行。

### 4. Token 與時間爆炸風險預估 (Cost & Latency Forecast)
*   **技術挑戰**：在不發送 API 的情況下難以精確預測生成長度。
*   **MVP 策優**：初期採用「檔案行數 + 依賴深度」作為代理指標。
*   **高風險特徵**：單一步驟預估 Token > 120k、或需要連續呼叫 LLM 超過 8 次。
*   **決策**：直接降級為「人類監督模式」或「分階段交接」。在 Pre-flight 階段就先警告：「本次任務預估消耗 280k Token，建議先做 PoC 確認可行後再全量執行。」這讓 Agent 真正具備「商業自我認知」。

### 4. Token 與時間爆炸風險預估 (Cost & Latency Forecast)
*   **高風險特徵**：單一步驟預估 Token > 120k、或需要連續呼叫 LLM 超過 8 次。
*   **決策**：直接降級為「人類監督模式」或「分階段交接」。在 Pre-flight 階段就先警告：「本次任務預估消耗 280k Token，建議先做 PoC（Proof of Concept）確認可行後再全量執行。」這讓 Agent 真正具備「商業自我認知」。

## ⚖️ Pre-flight Scoring Engine (最終評分模型)
我們將導入一套量化公式來評估每一次的計畫強度：
`總風險分數 = w1·Dependency + w2·ContextSpan + w3·SkillGap + w4·CostForecast`

**執行防護機制：**
*   **若總分 ≥ 7**：強制切換至 `/aa-orchestrate` + 小步測試 (Small step verification)。
*   **若總分 ≥ 10**：直接建議「人類介入 (Human Intervention)」並準備交接 (Handoff)。

## 🛡️ 安全與資安考量
*   確保每一次 Sub-task 切換時，不會遺失關鍵的資安上下文（如 Zero Trust rule）。我們將引入一個 `SECURITY_STRICT.md` 短文件，在任務切割時強制隨附。

## 🔍 第三方庫與工具
*   維持現有的 Bash、PowerShell 分析。
*   可能需要引入 `tiktoken` (若為 OpenAI) 或類似的 Token 計算演算法來做精準的本地測量，或者直接基於「檔案行數」與「依賴深度」做啟發式 (Heuristic) 預估。

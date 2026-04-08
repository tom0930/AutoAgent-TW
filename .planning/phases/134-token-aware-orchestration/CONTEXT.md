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
*   `running_temp` 負責**狀態持久化 (State Persistence)**（記錄 Checkpoint，供 `/aa-resume` 使用）。
*   本階段新增的機制負責**成本效益決策 (Cost/Capability Routing)**。可以在工作流開頭加入一個 `Token Evaluator` 的判斷節點。

## 🛡️ 安全與資安考量
*   確保每一次 Sub-task 切換時，不會遺失關鍵的資安上下文（如 Zero Trust rule）。我們將引入一個 `SECURITY_STRICT.md` 短文件，在任務切割時強制隨附。

## 🔍 第三方庫與工具
*   維持現有的 Bash、PowerShell 分析。
*   可能需要引入 `tiktoken` (若為 OpenAI) 或類似的 Token 計算演算法來做精準的本地測量，或者直接基於「檔案行數」與「依賴深度」做啟發式 (Heuristic) 預估。

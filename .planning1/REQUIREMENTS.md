# 需求清單 (REQUIREMENTS)

## Req 1: 子代理系統與平行任務調度 (v1.9.0)
- REQ-1.1: 實作 `SubagentSpawnManager` 以管理獨立 Python 子程序的生命週期。
- REQ-1.2: 實作 `Coordinator` 負責高層級目標的動態拆解（Research -> Synthesis -> Verification）。
- REQ-1.3: 新增 `/aa-orchestrate` 指令管理子代理調度。

## Req 2: MCP 協議整合層 (v2.0.0)
- REQ-2.1: 實作 `MCPClient` 以支援 stdio / sse 協議連線。
- REQ-2.2: 實作 `MCPToolRegistry` 作為統一工具註冊中心。
- REQ-2.3: 支援載入 `.agents/mcp_servers.json`。
- REQ-2.4: 新增 `/aa-mcp` 指令群。

## Req 3: 工作流客製化系統 (v2.1.0)
- REQ-3.1: 載入專案根目錄嘅 `CLAUDE.md` 規範以供 AutoAgent-TW 使用。
- REQ-3.2: 實作 `SkillLoader` 掃描與動態註冊 Markdown 格式腳本技能。
- REQ-3.3: 實作 `HookManager` 攔截 AutoAgent-TW 生命週期事件。
- REQ-3.4: 新增 `/aa-skill` 及 `/aa-hook` 指令群。

## Req 4: 專案記憶與上下文管理 (v2.2.0)
- REQ-4.1: 建立 `MemoryStore` 存儲 L1/L2/L3 分層記憶。
- REQ-4.2: 實作基於 embeddings 與 tags 的向量檢索 (Faiss叢集)。
- REQ-4.3: 實作 `ContextCompressor` 處理上下文自動壓縮避免 token 上限。
- REQ-4.4: 新增 `/aa-memory` 指令群。

## Req 5: 智慧指令預測引擎 (v2.3.0)
- REQ-5.1: 實作 `ContextTracker` 持續記錄文件、git及系統狀態追蹤。
- REQ-5.2: 實作 `CommandPredictor` 預測後續推薦操作。
- REQ-5.3: 新增 `/aa-predict` 指令。

## Req 6: 無頭模式與 CI/CD 整合 (v2.4.0)
- REQ-6.1: 實作 `HeadlessRunner` 支援非互動式調用與 Webhook。
- REQ-6.2: 撰寫預設 GitHub Actions `aa-agent.yml` 觸發腳本。
- REQ-6.3: 實作 `GitHubIntegration` 處理 PR review 評論與狀態報告。
- REQ-6.4: 新增 `/aa-headless` 指令群。

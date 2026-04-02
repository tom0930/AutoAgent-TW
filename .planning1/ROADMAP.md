# 發展路線圖 (ROADMAP)

## Phase 1: 子代理系統與平行任務調度 (v1.9.0)
- [X] 實作 SubagentSpawnManager (Asyncio based)
- [X] 實作 Coordinator 任務拆解引擎
- [X] 新增 `/aa-orchestrate` 指令支援
- [X] 更新 Dashboard 顯示子代理進度
- **狀態**: Completed (v1.9.0)

## Phase 2: MCP 協議整合層 (v2.0.0)
- [ ] 實作 MCPClient (stdio/sse)
- [ ] 實作 MCPToolRegistry 工具註冊
- [ ] 自動讀取 `.agents/mcp_servers.json`
- [ ] 新增 `/aa-mcp` 管理指令
- **狀態**: Not Started

## Phase 3: 工作流客製化系統 (v2.1.0)
- [ ] 加入 `CLAUDE.md` 專案規範自動載入
- [ ] 實作 SkillLoader 動態掛載 MD 技能
- [ ] 實作 HookManager 與生命週期事件綁定
- [ ] 新增 `/aa-skill`, `/aa-hook` 指令
- **狀態**: Not Started

## Phase 4: 專案記憶與上下文管理 (v2.2.0)
- [ ] 實作 MemoryStore (L1/L2/L3分層)
- [ ] 實作 ContextCompressor 動態壓縮對話與存儲
- [ ] 整合 faiss-cpu 進行記憶檢索
- [ ] 新增 `/aa-memory` 指令
- **狀態**: Not Started

## Phase 5: 智慧指令預測引擎 (v2.3.0)
- [X] 實作 ContextTracker 用於上下文追蹤
- [X] 實作 CommandPredictor 根據上下文提供建議
- [X] 更新 Dashboard 顯示推薦腳步
- [X] 新增 `/aa-predict` 指令
- **狀態**: Completed (v2.3.0)

## Phase 6: 無頭模式與 CI/CD 整合 (v2.4.0)
- [ ] 實作 HeadlessRunner
- [ ] 整合 GitHub API (GitHubIntegration) 用於自動檢閱與 Commit
- [ ] 產出 GitHub Actions 範本
- [ ] 新增 `/aa-headless` 管理指令
- **狀態**: Not Started

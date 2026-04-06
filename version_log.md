# AutoAgent-TW Version Log

## [v2.6.0-mcp-orchestrator] - 2026-04-07

### 🚀 新增功能 (Key Features)
1. **MCP Protocol Integration Layer (Phase 125)**: 實施 Model Context Protocol (MCP) 客戶端管理架構。支援 Stdio 傳輸協議與並行伺服器啟動，解決子代理「有大腦無工具」的斷層。
2. **MCP Tool Registry (NRT)**: 具備命名空間的工具註冊表 (`server::tool`)。整合 `langchain-mcp-adapters` 並修復 `Missing transport key` 配置缺陷，支援 17+ 跨平台自動化工具。
3. **ReAct Orchestration Loop**: 升級 `OrchestrationCoordinator` 以支援 LangGraph `ToolNode`。提供最多 5 輪的自主規劃與工具調用循環（ReAct），具備自動報錯與重試機制。
4. **MCP 視覺化儀表板 (Dashboard v2)**: 在 `status.html` 整合 MCP Toolkit 標籤。即時監控連線伺服器健康度 (🟢/🔴)、工具總數與調用詳細日誌。
5. **內建自動化工具集 (Internal MCP)**: 部署 `autoagent-internal` 伺服器，將 Phase 查詢、排程管理與狀態報告封裝為標準 MCP 工具。

### 📁 核心文件更新 (@file:)
- `src/core/mcp/mcp_client.py`: 並行連線管理器與 `load_mcp_tools` 修正 (v1.9.2 Bridge)。
- `src/core/mcp/registry.py`: 具備命名空間的工具註冊與 Schema 解析。
- `scripts/aa_mcp.py`: 統一的 MCP 管理 CLI (list/status/test)。
- `src/core/orchestration/coordinator.py`: 升級支援 ReAct 循環與動態工具節點。
- `scripts/mcp_internal_server.py`: 內建 FastMCP 伺服器實作。
- `.agents/mcp_servers.json`: 安全化的 MCP 伺服器配置文件。
- `.agents/skills/status-notifier/templates/status.html`: 儀表板 MCP Toolkit 功能模組。

### 🔒 安全性 (Security)
- Guardian Scan: ALL PASS (已實施 Root Path 限制與環境變數脫敏)。
- 支援 IRA 5-Level 權限管制：MCP 工具調用自動注入風險評估欄位。


## [v2.5.0-context-defense] - 2026-04-05

### 🚀 新增功能 (Key Features)
1. **Active Context Defense (ACD)**: 根治 Antigravity 工作區 Max Token Limit Error。自動掃描工作區檔案大小分佈、預估 Token 佔用、生成 `.geminiignore` 排除二進位與編譯產物。
2. **Context Guard Pre-scan**: `/aa-plan` 新增 Step 0 前置檢查，在載入任何上下文前先驗證 Token 預算安全性。超過 100K tokens 即觸發告警。
3. **自動 .geminiignore 生成**: `/aa-new-project` 新增 Step 1.5，初始化專案時自動建立 `.geminiignore`，確保每個新專案從第一天就受到保護。
4. **Windows cp950 相容**: 所有 CLI 輸出改用 ASCII-safe 標記 + UTF-8 強制輸出，解決繁體中文 Windows 下的 emoji crash。

### 📊 關鍵數據 (Impact)
- **z:\ac 修復前**: 512 MB / 16,888 檔案 → Token 爆炸 (800K+ tokens)
- **z:\ac 修復後**: `.geminiignore` 排除後僅索引 ~13 MB 原始碼 → 安全範圍

### 📁 新增/修改文件 (@file:)
- `scripts/context_guard.py`: Context Guard 核心掃描引擎 (220 lines)。
- `.geminiignore`: AutoAgent-TW 工作區 Antigravity 索引排除規則。
- `z:\ac\.geminiignore`: OpenClaw 工作區即時修復。
- `_agents/workflows/aa-plan.md`: 新增 Step 0 Context Guard pre-scan。
- `_agents/workflows/aa-new-project.md`: 新增 Step 1.5 自動生成 .geminiignore。
- `.planning/phases/123-context-guard/CONTEXT.md`: 根因分析與設計決策。
- `.planning/phases/123-context-guard/GUARD-REPORT.md`: 安全掃描報告 (ALL PASS)。
- `.planning/phases/123-context-guard/QA-REPORT.md`: 品質驗證報告 (7/7 UAT PASS)。

### 🔒 安全性 (Security)
- Guardian Scan: ALL PASS (零洩漏、零注入風險)
- 1 個 LOW-risk finding: `shell=True` 於靜態 `npm.cmd install` 命令（已標註）


## [v2.4.0-final-bridge] - 2026-04-04

### 🚀 新增功能 (Key Features)
1. **IDE-Bridge 指令轉發 (Brain Delegation Mode)**: 實施具備 FastAPI 後端的 `aa-bridge` 代理伺服器。允許外部 AI 代理 (如 OpenClaw) 無縫存取 Antigravity IDE 內建的 AI 推理能力，解決本地 API Key 缺失與跨項目模型共享難題。
2. **OpenClaw 全方位集成 (Standalone Decoupling)**: 安裝程式現在支持 OpenClaw 核心的動態部署。自動修復 Metadata 遺失與硬編碼路徑依賴，建立基於 `OPENCLAW_HOME` 的可移植性架構。
3. **全域指令集擴充 (CLI Ecosystem)**: 新增 `autoagent` (主控)、`openclaw-skills` (技能管理) 與 `aa-bridge` (大腦中轉) 三大核心指令，並自動註冊至系統 PATH。
4. **AutoSkills 自我進化引擎 (Evolution Engine)**: 實施全自動的技能健檢與重產機制。系統會監控技能成功率，當低於 85% 時自動啟動進化循環以修補缺陷。

### 📁 核心文件更新 (@file:)
- `scripts/aa_installer_logic.py`: 大幅更新安裝邏輯，包含核心 `src/` 部署、OpenClaw 地區化拷貝與全域指令註冊。
- `src/bridge/ai_proxy.py`: IDE-Bridge 核心代理實作。
- `aa-bridge.cmd` & `openclaw-skills.cmd`: 全域啟動腳本。
- `src/agents/skills/skill_metrics.py`: 技能健康度追蹤核心。
- `src/cron/skill_evolution.py`: 技能自動進化引擎。
- `.planning/phases/122-openclaw-bridge-installer/`: 研發計畫與驗證報告 (PLAN/QA)。

## [v2.3.0-autoskills-security] - 2026-04-04

### 🚀 新增功能 (Key Features)
1. **IRA 5 級權限系統 (Interactive Requirement Analysis)**: 建立動態工具風險管制閘道。支援 5 級風險分級 (Fatal, High, Medium, Low, Read)，針對高風險操作自動觸發 LangGraph 中斷與人工審核。
2. **AutoSkills 自動技能引擎 (Skill Orchestration)**: 實施 Skill Package v2 規範。支援基於 `manifest.json` 的權限宣告與 Zod-like (Pydantic) 靜態驗證。
3. **動態技能生成與搜尋 (Discovery & Generation)**: 提供 `skills.discover` 與 `skills.generate` 工具，能根據任務意圖自動搜尋本地/遠端技能或動態產生符合規範的技能包。
4. **安全沙盒驗證 (Sandbox Tester)**: 在安裝前自動化驗證技能行為，確保腳本執行不超出宣告權限範圍。

### 📁 新增/修改文件 (@file:)
- `src/core/state.py` & `src/core/graph.py`: IRA 核心狀態機與 LangGraph 守衛節點。
- `src/core/permission_engine.py`: 工具風險等級註冊與中斷邏輯。
- `src/core/skill_manifest.py`: Skill Package v2 Pydantic Schema 定義。
- `src/agents/tools/skills_discover.py` & `src/agents/tools/skills_generate.py`: 技能發現與生成引擎。
- `src/agents/skills/skill_sandbox_test.py`: 技能安全性與行為動態驗證器。
- `src/cli/openclaw_skills.py`: 統一的 AutoSkills 管理命令集 (Discover/Generate/Test)。
- `.planning/phases/120-ira-permission-system/`: 完整的研發文檔 (PLAN/RESEARCH/QA)。

## [v2.2.0-pisrc-resilience] - 2026-04-03

### 🚀 新增功能 (Key Features)
1. **PISRC 自我修復框架 (Persistent Issue Self-Review & Correction)**: 基於 LangGraph 的有狀態圖架構，取代傳統靜態迴圈。支援多層級反思與 5-Whys 根因分析。
2. **Installer 安全性加固 (Installer Hardening)**: 徹底解決 Windows 下 `setx` 環境變數長度上限、PID 爆炸以及跨項目狀態污染等關鍵部署漏洞。
3. **異步持久化中斷 (Human-in-the-Loop)**: 圖狀態自動持久化，失敗時掛起並等待人工介入，支援斷點續傳。

### 📁 新增/修改文件 (@file:)
- `scripts/resilience/pisrc_graph.py`: PISRC 核心圖結構與節點實作。
- `scripts/aa_installer_logic.py`: 安裝與環境設置邏輯修復。
- `_agents/workflows/aa-fix.md`: 全面改接 LangGraph PISRC 診斷邏輯。
- `requirements.txt` & `build_requirements.txt`: 引入 `langgraph`, `langchain-core` 並解耦打包工具。
- `.planning/phases/119-pisrc-installer-integration/`: 完整研發週期文檔。

## [v2.1.0-custom-workflow] - 2026-04-02

### 🚀 新增功能 (Key Features)
1. **工作流客製化系統 (Workflow Customization)**: 透過 `CLAUDE.md` 自動注入項目約束規約。
2. **動態生命週期鉤子 (Lifecycle Hooks)**: 支援 `.agents/hooks.json` 配置，自動執行 Lint、Ruff 與自動修復。
3. **Markdown 技能掛載 (Skill Loader)**: 掃描 `.agents/skills/*.md` 動態擴展示系統指令，無需修改核心。
4. **重入保護鎖 (Re-entry Guard)**: 異步事件執行安全性加固，防止 Hook 無限循環。
5. **管理指令集 (CLI)**: 新增 `/aa-skill` (技能查看) 與 `/aa-hook` (鉤子管理) 指令。

### 📁 新增/修改文件 (@file:)
- `scripts/hooks/hook_manager.py`: 重構 Hook 核心以支援 JSON 配置。
- `scripts/skills/skill_loader.py`: 實作 MD 技能解析與自動發現。
- `scripts/config/claude_loader.py`: 實作 CLAUDE.md 規約載入。
- `scripts/aa_skill_cli.py` & `scripts/aa_hook_cli.py`: 管理 CLI 工具。
- `.agents/hooks.json`: 初始 Hook 配置文件。
- `CLAUDE.md`: 項目規約範本。
- `.planning1/phases/003-workflow-customization/`: 完整的研發文檔 (CONTEXT/RESEARCH/PLAN/QA/SUMMARY)。

---

## [v1.5.0-v0.3-transparency] - 2026-03-31

### 🚀 新增功能 (Key Features)
1. **即時視覺化儀表板 (Status Dashboard)**: 提供執行進度、下一步目標與狀態顯示。
2. **動態執行樹 (Execution Tree)**: 使用 Mermaid.js 自動渲染 ROADMAP.md 的開發路徑。
3. **即時日誌流 (Live Logs)**: 在瀏覽器中直接查看 Agent 運作日誌，含滑入動畫。
4. **停滯偵測與 LINE 警報 (Stagnation & Alerts)**: 90 秒執行無回應警告及 LINE Notify 遠端推送。
5. **多端同步 (Backend State Sync)**: Python Backend 同步狀態至 JSON/JS，繞過 CORS 與緩存限制。

### 📁 新增/修改文件 (@file:)
- `.agents/skills/status-notifier/SKILL.md`: 技能說明與集成指南。
- `.agents/skills/status-notifier/scripts/status_updater.py`: 狀態更新與狀態機推動核心。
- `.agents/skills/status-notifier/scripts/roadmap_parser.py`: ROADMAP Markdown 轉 Mermaid Parser。
- `.agents/skills/status-notifier/scripts/line_notifier.py`: LINE Notify API 接口。
- `.agents/skills/status-notifier/templates/status.html`: 視覺化 Dashboard 前端 (Tailwind + Lucide + Mermaid)。
- `_agents/workflows/aa-progress.md`: 注入儀表板刷新與連結顯示邏輯。
- `README.md`: 更新開發版本資訊與功能介紹。
- `.planning/`: 完整的項目研發流程文件 (PROJECT/ROADMAP/STATE/PHASES)。

### 🛠 技術細節 (Technical Details)
- **CORS Fix**: 採用 Script Inject 模式 (`window.AA_STATUS`) 解決 `file://` 協定下的安全性限制。
- **Encoding Fix**: 在 Windows 環境強制 Python 使用 UTF-8 reconfigure `stdout` 以支援表情符號輸出。
- **Visual Polish**: 採用 Glassmorphism 設計語法，提升自動化代理的執行透明度。

---
*Generated by AutoAgent-TW*

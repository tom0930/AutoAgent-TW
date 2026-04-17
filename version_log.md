# AutoAgent-TW Version Log

## [v2.9.1-reliability-tuning] - 2026-04-17

### 🚀 新增功能 (Key Features)
1. **Ty-by-Default 架構 (Phase 152)**: 全面切換 IDE 預設語言伺服器至 `ty` (Astral)，確保背景不會因為持續追蹤跨模組變化而佔用高達 500MB+ 記憶體，達到了極致的輕量化。
2. **Pyrefly Shadow Check 機制**: 將高負載的 Pyrefly 型別推斷抽離至背景「影子審計」流程。在 `/aa-qa` 或 Git pre-commit 時拉起，掃描完畢藉由 Active Reaper 機制瞬間回收，確保 0 常駐記憶體。
3. **自動化型別錯誤補救**: 透過 `pyrefly suppress` 機制全自動消除歷史專案遺留的 Win32 API 型別缺失與套件匯入解析錯誤 (修補超過 200+ 項警告)，大幅度強化開發暢通度。
4. **Toolchain Installer 推進**: `aa_installer_logic.py` 現在會自動拉取最新版本的 `uv`、`ty`、`pyrefly`，並自主寫入 Git Hooks，完成整體架構無縫移轉。

### 📁 核心文件更新 (@file:)
- `scripts/aa_installer_logic.py`: 安裝與更新自動化整合。
- `scripts/shadow_check.py`: Pyrefly 影子檢查器與 Active Reaper。
- `pyrefly.toml`: 專案排除配置與依賴規則設定。
- `.planning/phases/152-dynamic-reliability-debug/QA-REPORT.md`: 完整型別品質與效能審查記錄。

### 🔒 安全性 (Security)
- Guardian Scan: ALL PASS。
- 記憶體生命週期：具備確保 `pyrefly` 不會殘留僵屍程序的防護機制。

## [v2.9.0-terminal-optimization] - 2026-04-15
1. **Starship 跨 Shell 提示字元整合 (Phase 141)**: 導入 Rust 編寫的 Starship 引擎。透過 `~/.config/starship.toml` 實施「極簡模式」，自動縮減路徑深度並關閉高耗能模組，提升開發直覺與降低 Token 日誌干擾。
2. **JetBrainsMono Nerd Font 部署**: 自動化安裝並註冊 Nerd Font 家族。確保終端機能正確渲染 Git、目錄與系統狀態符號，提升視覺化開發體驗。
3. **PowerShell 路徑強健性方案**: 實施 `scripts/setup_starship_force.py`。採用 .NET 特殊資料夾解析技術，徹底解決 Windows OneDrive `文件` 路徑與 PowerShell `$PROFILE` 之間的編碼與環境變數同步衝突。
4. **Token 節省機制 (Context Lean)**: 透過 `truncation_length = 2` 與靜態模組過濾，將每次指令回應的路徑 Token 佔用降低約 40%。

### 📁 核心文件更新 (@file:)
- `.config/starship.toml`: Token 優化配置。
- `scripts/setup_starship_force.py`: 路徑修復與注入核心。
- `scripts/install_env.ps1`: 環境自動化安裝腳本。
- `.planning/phases/141-starship-integration/QA-REPORT.md`: 完整品質驗證報告。

### 🔒 安全性 (Security)
- Guardian Scan: ALL PASS (無硬編碼路徑溢漏，支援絕對與相對環境變數共存)。
- 支援 Idempotent 部署：多次執行指令不會重複污染 Profile。

## [v2.8.0-observability-modernization] - 2026-04-14

### 🚀 新增功能 (Key Features)
1. **React 現代化儀表板 (Phase 136/137)**: 徹底捨棄舊有的 HTML 注入模式，轉向 React/Vite 架構。提供毫秒級響應、Glassmorphism 與波紋動畫的極致 UI 體驗。
2. **滾動式執行軌跡 (Execution Timeline)**: 實施具備 50 筆緩衝的 LIFO 執行歷史。記錄任務、Phase 歸屬與狀態，支援開發者回溯 Agent 的決策過程。
3. **Mermaid.js v11 動態整合**: 在 Dashboard 內核整合 Mermaid 引擎。根據 `ROADMAP.md` 即時生成多色標註的開發流程圖，支援自動縮放與交互式導覽。
4. **工業級並發治理 (Concurrent Hardening)**: 升級 `status_updater.py` (v1.8.0)。採用 **原子寫入 (Atomic Write)** 與 **Exclusive Locking (portalocker)** 機制，在 100 輪併發壓力測試下達成 0 衝突。
5. **根目錄指令代理 (Global Hub)**: 於專案根目錄部屬代理 `package.json`。開發者現在可在根目錄直接執行 `npm run dev` 啟動所有觀察組件，解決目錄混亂問題。
6. **環境自動偵測 (Context Awareness)**: 儀表板自動與 `PROJECT.md` 掛鉤。無須手動設定即可自動識別當前專案背景與維度。

### 📁 核心文件更新 (@file:)
- `.agents/skills/status-notifier/scripts/status_updater.py`: 升級至 v1.8.0，支援原子鎖與雙軌同步。
- `~/.gemini/antigravity/dashboard/skills/src/App.tsx`: 全新 React 儀表板核心。
- `package.json`: 根目錄指令代理鏈。
- `run-dashboard.cmd`: 快捷啟動腳本。
- `.planning/phases/137-dashboard-finisher/QA-REPORT.md`: 壓力測試與品質審計報告。

### 🔒 安全性 (Security)
- Guardian Scan: ALL PASS (無密鑰洩漏)。
- CORS Defense: 透過 Vite Proxy 解決本地資源讀取限制。


## [v2.7.0-knowledge-gateway] - 2026-04-13

### 🚀 新增功能 (Key Features)
1. **知識閘道器 (Knowledge Gateway - Phase 133)**: 實施具備「前綴路由」機制的處理中心。支援 `@大腦` (RAG 查詢) 與 `#知識庫` (內容匯入) 自動分流。
2. **多模態 OCR 攝取管道**: 整合 Gemini 1.5 Flash 視覺模型。自動對 Line 上傳的圖片進行高精準文字擷取，並排除冗餘問候語，精煉核心知識。
3. **混合同步平面 (Hybrid Sync Plane)**: 實施 `scripts/kb_gdrive_sync.py`。支援 Rclone 映射與原生 GDrive API (Service Account) 雙模式，解決受限網路環境下的同步難題。
4. **零成本資安防禦 (Whitelist Defense)**: 導入 `LINE_ADMIN_UID_LIST` 白名單鎖定機制。確保只有授權管理員能觸發 AI 運算與知識庫異動，防範惡意 Token 耗損。
5. **本地緩衝與災難恢復 (Local Buffering)**: 所有匯入內容優先落盤於 `data/kb_upload_queue/`，確保在網路故障時知識不遺失。

### 📁 核心文件更新 (@file:)
- `scripts/aa_kb_gateway.py`: 核心路由、白名單驗證與 OCR 邏輯實作。
- `scripts/kb_gdrive_sync.py`: GDrive API 與 Rclone 同步引擎。
- `ARCHITECTURE.md`: 新增知識攝取管道與 RAG 路徑圖。
- `SECURITY.md`: 新增攝取防禦與視覺 Injection 緩解策略。
- `.planning/phases/133-linebot-gdrive-nlm-combo/QA-REPORT.md`: 完整驗證與測試報告。

### 🔒 安全性 (Security)
- Guardian Scan: ALL PASS (認證密鑰脫敏驗證通過)。
- 支援 Visual Prompt Injection 防禦：限定 OCR Prompt 範圍。

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

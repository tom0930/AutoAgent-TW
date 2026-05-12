# Graph Report - src  (2026-05-12)

## Corpus Check
- 103 files · ~44,773 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1456 nodes · 2930 edges · 55 communities detected
- Extraction: 67% EXTRACTED · 33% INFERRED · 0% AMBIGUOUS · INFERRED: 958 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]

## God Nodes (most connected - your core abstractions)
1. `HarnessGateway` - 59 edges
2. `KnowledgeGraph` - 55 edges
3. `PalaceIndex` - 55 edges
4. `SessionManager` - 43 edges
5. `WorkflowEvent` - 43 edges
6. `HarnessCLI` - 37 edges
7. `EventType` - 36 edges
8. `CronScheduler` - 34 edges
9. `Entity` - 34 edges
10. `SearchResult` - 34 edges

## Surprising Connections (you probably didn't know these)
- `HarnessGateway` --uses--> `AI Harness Health Check System Provides comprehensive system diagnostics for th`  [INFERRED]
  core\harness_gateway.py → core\health\checks.py
- `HarnessGateway` --uses--> `Multi-subsystem health checker for AI Harness.     Run all checks or specific c`  [INFERRED]
  core\harness_gateway.py → core\health\checks.py
- `HarnessGateway` --uses--> `Run all health checks.`  [INFERRED]
  core\harness_gateway.py → core\health\checks.py
- `HarnessGateway` --uses--> `Run all health checks and return exit code (0=healthy, 1=issues).`  [INFERRED]
  core\harness_gateway.py → core\health\checks.py
- `SkillRollbackManager` --calls--> `main()`  [INFERRED]
  agents\skills\skill_rollback.py → cli\openclaw_skills.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.02
Nodes (126): Memory Module - Hybrid Palace Architecture  Layer 1: Working Memory (OpenClaw-, create(), Entity, EntityQuery, EntityType, from_dict(), KGConfig, KnowledgeGraph (+118 more)

### Community 1 - "Community 1"
Cohesion: 0.03
Nodes (55): Perform a robust GUI automation action on the target element.     Uses UIA fast, rva_click(), ContextMonitor, Observer-based UI state monitor using Smart Polling.     Eliminates dependency, Wait until a window matching title_re appears., Wait until a specific element exists in the target window.         kwargs are p, Generic wait for an arbitrary boolean condition., Named Pipe Server for Vision Engine control signals. (+47 more)

### Community 2 - "Community 2"
Cohesion: 0.04
Nodes (67): CLIEventRenderer, Renders Workflow Events to the CLI using Rich.     Provides a dynamic 'dashboar, ExitCode, Standardized exit codes for AutoAgent-TW CI/CD and Headless execution., AI Harness Gateway - 守護行程服務 功能：啟動時自動初始化所有服務，支援 start/stop/restart/status 命令 版本, Initialize concrete service module based on service_id.         Routes to the a, Initialize the Security Sentinel service., Initialize the MemPalace memory service. (+59 more)

### Community 3 - "Community 3"
Cohesion: 0.03
Nodes (51): AgentReaper, Industrially prunes orphaned agent and MCP processes.     Identifies 'AutoAgent, Helper to safely extract process info., Recursively kills a process and all its children., AgentState, Expanded Agent State for LangGraph Orchestration with a dynamic      5-level to, MCPClientManager, AutoAgent-TW MCP Client Manager v2 - asyncio.gather 並行啟動所有 server（避免單一 server 阻 (+43 more)

### Community 4 - "Community 4"
Cohesion: 0.04
Nodes (29): AI Harness CLI Package, HarnessCLI, main(), AI Harness CLI - Unified command-line interface Version: v3.5.5  Usage:, Gateway commands: start/stop/restart/status., Cron/scheduler commands., Node/device pairing commands., Vision system commands. (+21 more)

### Community 5 - "Community 5"
Cohesion: 0.07
Nodes (42): AutoCompressor, Asynchronous Context Compression Worker.     Implements the 3-stage (L1->L2->L3, Starts the compression pipeline in a background thread., CompressionQualityGate, QualityGateResult, The 'Hard Gate' for AI context compression.     Ensures that compressed summari, Validates the compression quality across 3 dimensions., CompressionSummary (+34 more)

### Community 6 - "Community 6"
Cohesion: 0.04
Nodes (32): call_antigravity_ide(), chat_completions(), gemini_relay(), Gemini 視覺轉發器：將 RVA Engine 的截圖轉發給本地 Port 8045, 對接截圖所示的本地 Antigravity Tools (Port 8045):, HealthChecker, HealthCheckResult, HealthLevel (+24 more)

### Community 7 - "Community 7"
Cohesion: 0.05
Nodes (26): AI Harness Core Package 所有 AI Harness 核心模組 版本：v1.0.0, AI Harness Cron Package (legacy root-level redirect) All cron functionality is, CronJob, CronParser, CronScheduler, JobKind, JobRun, JobStatus (+18 more)

### Community 8 - "Community 8"
Cohesion: 0.05
Nodes (34): int, compress_content(), CompressionConfig, CompressionResult, estimate_tokens(), Token Compression - Q4_K_M Style Local Model Compression  Implements token-awa, Estimate token counts for multiple chunks., Parse markdown structure for structure-aware compression. (+26 more)

### Community 9 - "Community 9"
Cohesion: 0.05
Nodes (17): ABC, BaseRenderer, MCPTool, MCPToolCall, MCPToolResult, MCPTransportBase, AI Harness MCP Hub 功能：MCP (Model Context Protocol) 伺服器發現、路由、代理 版本：v1.0.0, 呼叫 MCP Tool                  Args:             call: Tool 呼叫請求 (+9 more)

### Community 10 - "Community 10"
Cohesion: 0.07
Nodes (29): BaseModel, main(), FileSystemPermissions, GUIPermissions, NetworkPermissions, Skill Package v2 Manifest Schema (AutoSkills Phase 2 - Task 1.1)., SkillManifest, SkillPermissions (+21 more)

### Community 11 - "Community 11"
Cohesion: 0.07
Nodes (21): FlushEvent, Working Memory Module - Layer 1 of Hybrid Palace Architecture  Manages short-t, Flush working memory content to long-term storage.                  Args:, Compress content to target token count.                  Phase 1: Structure-aw, Estimate token count.                  Rough approximation:         - English, Append content to file, creating if needed, Load MEMORY.md content (long-term curated memory), Load daily memory file content (+13 more)

### Community 12 - "Community 12"
Cohesion: 0.09
Nodes (14): main(), Monitor, AI Harness Vision Engine 功能：螢幕截圖、即時錄製、滑鼠/鍵盤控制、CDP 整合 版本：v1.0.0, 截圖並儲存到檔案                  Args:             path: 輸出檔案路徑             region:, 擷取特定視窗                  Args:             window_title: 視窗標題（支援部分匹配）, 啟動連續截圖                  Args:             interval: 截圖間隔（秒）, 取得最新一幀（需先呼叫 start_continuous_capture）, 比較兩個區域的畫面相似度                  Returns:             相似度 (0-1) (+6 more)

### Community 13 - "Community 13"
Cohesion: 0.13
Nodes (12): CanvasEdge, CanvasNode, CanvasSnapshot, CanvasSystem, main(), NodeStatus, NodeType, AI Harness Canvas System 功能：視覺化狀態管理、節點狀態、圖形渲染 版本：v1.0.0 (+4 more)

### Community 14 - "Community 14"
Cohesion: 0.11
Nodes (12): AgentConfig, AgentResult, AgentRuntime, AgentSpawner, AgentStatus, main(), AI Harness Agent Spawner 功能：子代理管理、並行執行、任務分派 版本：v1.0.0, Spawn 子代理                  Args:             prompt: 代理任務提示             runt (+4 more)

### Community 15 - "Community 15"
Cohesion: 0.13
Nodes (12): AI Harness Node Package, DevicePairing, DeviceType, main(), NodePairing, PairingStatus, AI Harness Node Pairing 功能：設備配對管理、安全驗證、狀態同步 版本：v1.0.0, 初始化配對流程                  Args:             device_type: 設備類型             dev (+4 more)

### Community 16 - "Community 16"
Cohesion: 0.12
Nodes (12): AI Harness Messages Package, ChannelAdapter, main(), Message, MessageChannel, MessagePriority, MessageResult, MessageRouter (+4 more)

### Community 17 - "Community 17"
Cohesion: 0.11
Nodes (16): compile_ira_graph(), gatekeeper_node(), log_contract(), Compiles the IRA 5-Level Permission Graph with SqliteSaver persistence., Appends the signed contract to a local JSONL file for non-repudiation., IRA 5-Level Permission Guard Node (Phase 120 - Task 2.2 / 3.2).     Includes La, Mock Tool Executor with Phase 153 Hash Verification., tool_executor_node() (+8 more)

### Community 18 - "Community 18"
Cohesion: 0.15
Nodes (8): FeedbackManager, Manages user feedback (Thumbs Up/Down) for AI suggestions (Phase 171 v2.1)., Calculates user satisfaction metrics., High-level engine to generate context-aware, evidence-linked suggestions (Phase, Deep analysis of a 'CRISIS' event.         Returns a high-confidence suggestion, Calculates how 'annoying' the AI should be based on feedback., Zero-cost (L0) scanner using regex/rules (Phase 171 v2.1).         Detects code, SuggestionEngine

### Community 19 - "Community 19"
Cohesion: 0.13
Nodes (5): DashboardController, Controller for the /aa-dashboard command (Phase 171 v2.1).     Renders telemetr, Aggregates metrics for the dashboard., Observability System for Multi-Agent Operations (Phase 171 v2.1).     Tracks Sq, TelemetryManager

### Community 20 - "Community 20"
Cohesion: 0.18
Nodes (5): FeatureFlags, Simple Feature Flag management system.     Supports JSON config file with envir, Returns True if the flag is enabled., Returns the value of the flag., Sets a flag value and optionally persists it to JSON.

### Community 21 - "Community 21"
Cohesion: 0.21
Nodes (4): Enforce strict 900s timeout., Log operations for repudiation protection., Compute MD5 of an image footprint to detect UI jitter/staleness., RVAAuditContext

### Community 22 - "Community 22"
Cohesion: 0.18
Nodes (5): ContextScoper, Filters the base context to only include information relevant to the target file, Determines if the context should be compressed., Simple heuristic for token estimation., Manages context window optimization for CI/CD environments (Stealth Mode).

### Community 23 - "Community 23"
Cohesion: 0.27
Nodes (6): Checks if the given file path matches any glob pattern in the whitelist., Raises PermissionError if access is denied., Utility function for quick tool-level interception., Logical VFS Sandbox for AutoAgent-TW Subagents.     Enforces path-based access, validate_access(), VFSGuard

### Community 24 - "Community 24"
Cohesion: 0.22
Nodes (4): HeadlessRuntime, Enable headless mode hooks., Intercepts input() calls. Returns default_input or reads from stdin         if, Overrides interactive behaviors for CI/CD environments.     Prevents blocking i

### Community 25 - "Community 25"
Cohesion: 0.28
Nodes (4): 尋找 Console 控制項 (通常是 RichEdit20W 或類似類名), 阻塞並等待關鍵字出現 (如 'Programming succeeded'), Xilinx/Vitis Console Tracker     透過 pywinauto 直接掛載進 IDE 的 Console 視窗，監控燒錄文字。, XilinxConsoleTracker

### Community 26 - "Community 26"
Cohesion: 0.25
Nodes (4): install_ci_sanitizer(), LogSanitizerStream, Installs global stdout/stderr hooks to mask sensitive tokens in CI logs., Wraps a text stream and filters out sensitive patterns (API Keys, Tokens).

### Community 27 - "Community 27"
Cohesion: 0.25
Nodes (4): HeadlessRVAAdapter, Intercepts GUI actions and returns a dummy success or NotImplemented., Returns a placeholder image or empty bytes in headless mode., Stubs out RVA (Remote Visual Automation) features when running in Headless mode.

### Community 28 - "Community 28"
Cohesion: 0.29
Nodes (4): Evaluates a shell command risk.         Returns (is_allowed, reason, risk_level, Evaluates Python code for dangerous imports or calls., L5 Defense: Predicts risk of execution before it happens.     Simulates a 'Pre-, SandboxEvaluator

### Community 29 - "Community 29"
Cohesion: 0.4
Nodes (2): EvidenceMemory, Manages structured evidence facts in MemPalace L3.

### Community 30 - "Community 30"
Cohesion: 0.33
Nodes (2): MetricsExporter, Exports CI execution metrics to a structured JSON file.     Used for performanc

### Community 31 - "Community 31"
Cohesion: 0.4
Nodes (2): DiffScanner, Scans for changed files to enable incremental processing in CI.     Filters out

### Community 32 - "Community 32"
Cohesion: 0.67
Nodes (2): Scans for and terminates orphaned or stale components of the Antigravity stack., reap_orphaned_agents()

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (1): AI Harness Package - 統一 AI Agent 框架 版本：v1.0.0

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (1): Global limits for resource governance in CI.

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (1): Returns a list of files changed since the base_ref.

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (1): Filters out non-source files (e.g., .md, .png, .json).

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (1): Generates a sealed verification contract with a cryptographic hash.

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (1): Verifies if the current tool arguments match the sealed contract.         Preve

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (1): Get the inverse relation type.

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (1): Deserialize from dictionary.

### Community 42 - "Community 42"
Cohesion: 1.0
Nodes (1): Create a new entity with auto-generated ID.

### Community 43 - "Community 43"
Cohesion: 1.0
Nodes (1): Deserialize from dictionary.

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (1): Create a new relation with auto-generated ID.

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (1): Deserialize from dictionary.

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (1): Create a new drawer with auto-generated ID.

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (1): Deserialize from dictionary.

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (1): Create a new room with auto-generated ID.

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (1): Deserialize from dictionary.

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (1): Create a new wing with auto-generated ID.

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (1): Deserialize from dictionary.

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (1): Called when an individual agent changes state.

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (1): Renders a proactive AI suggestion with evidence.

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (1): Renders high-level squad performance/load.

### Community 55 - "Community 55"
Cohesion: 1.0
Nodes (1): Renders emergency intervention UI.

## Knowledge Gaps
- **301 isolated node(s):** `AutoSkills Health Metrics Collector (Phase 2 - Task 3.1).     Tracks success/fa`, `Records a single execution of a skill.`, `Calculates success rate and provides triage suggestions.`, `AutoSkills Rollback Manager (Phase 2 - Task 3.3).     Ensures that every skill`, `Backs up the current skill to an archive folder before an update.` (+296 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 29`** (6 nodes): `EvidenceMemory`, `.add_fact()`, `._generate_id()`, `.__init__()`, `.to_json()`, `Manages structured evidence facts in MemPalace L3.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (6 nodes): `MetricsExporter`, `.finalize()`, `.__init__()`, `.record_stage()`, `metrics_exporter.py`, `Exports CI execution metrics to a structured JSON file.     Used for performanc`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (5 nodes): `DiffScanner`, `filter_relevant_files()`, `get_changed_files()`, `diff_scanner.py`, `Scans for changed files to enable incremental processing in CI.     Filters out`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (3 nodes): `agent_reaper.py`, `Scans for and terminates orphaned or stale components of the Antigravity stack.`, `reap_orphaned_agents()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (2 nodes): `__init__.py`, `AI Harness Package - 統一 AI Agent 框架 版本：v1.0.0`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `Global limits for resource governance in CI.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `Returns a list of files changed since the base_ref.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `Filters out non-source files (e.g., .md, .png, .json).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `Generates a sealed verification contract with a cryptographic hash.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `Verifies if the current tool arguments match the sealed contract.         Preve`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (1 nodes): `Get the inverse relation type.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (1 nodes): `Deserialize from dictionary.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (1 nodes): `Create a new entity with auto-generated ID.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (1 nodes): `Deserialize from dictionary.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `Create a new relation with auto-generated ID.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `Deserialize from dictionary.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `Create a new drawer with auto-generated ID.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `Deserialize from dictionary.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `Create a new room with auto-generated ID.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `Deserialize from dictionary.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `Create a new wing with auto-generated ID.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `Deserialize from dictionary.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `Called when an individual agent changes state.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `Renders a proactive AI suggestion with evidence.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `Renders high-level squad performance/load.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (1 nodes): `Renders emergency intervention UI.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `HarnessGateway` connect `Community 4` to `Community 1`, `Community 2`, `Community 5`, `Community 6`, `Community 7`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._
- **Why does `AI Harness Core Package 所有 AI Harness 核心模組 版本：v1.0.0` connect `Community 7` to `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 6`, `Community 9`, `Community 15`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Why does `SessionManager` connect `Community 5` to `Community 4`, `Community 7`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `HarnessGateway` (e.g. with `InputSanitizer` and `AuditLogger`) actually correct?**
  _`HarnessGateway` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 29 inferred relationships involving `KnowledgeGraph` (e.g. with `RerankConfig` and `RerankResult`) actually correct?**
  _`KnowledgeGraph` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 29 inferred relationships involving `PalaceIndex` (e.g. with `RerankConfig` and `RerankResult`) actually correct?**
  _`PalaceIndex` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 47 inferred relationships involving `str` (e.g. with `.validate_full_skill()` and `.generate_skill_package()`) actually correct?**
  _`str` has 47 INFERRED edges - model-reasoned connections that need verification._
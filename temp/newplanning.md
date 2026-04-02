## 分析與方案

NEVER 洩露敏感數據（如 API key、密碼）到外部系統。
NEVER temp目錄不能git,
DO NOT 修改系統級文件（/etc, /usr）除非明確要求。

DO .planning目錄是舊方案，建新的.planning1目錄做下面新的專案

DO 新建的技能skill,prompt可以切換skill mode,不能指令太多使用者一次需查太多，command aa-skillmode

aa-skillmode low:一般使用者用常用的

aa-skillmode high:高級使用者開放全部

AutoAgent-TW 已具備排程、任務鏈、事件驅動等基礎骨架，但距離上述 6 階段完整工作流仍有顯著差距。以下直接產出完整方案文件：

```markdown
# cc_adv.md — AutoAgent-TW × Claude Code 六階段進階整合方案

> **檔案位置**: `.agents/skills/cc-adv/cc_adv.md`
> **版本**: v1.0.0
> **建立日期**: 2026-04-02
> **適用對象**: AutoAgent-TW v1.8.0+ 開發團隊

---

## 一、現狀差距總覽

| 階段 | 對應 Claude Code 優勢 | AutoAgent-TW 現狀 | 缺口等級 |
|------|----------------------|-------------------|---------|
| 1 | 自主代理與平行任務處理 | `/aa-chain` 條件管線，無真正子代理 | 🔴 高 |
| 2 | MCP 無限擴充性 | 無 MCP 任何實作 | 🔴 高 |
| 3 | 工作流客製化 | 僅硬編碼指令，無 CLAUDE.md / Hooks | 🟡 中 |
| 4 | 自動上下文壓縮與記憶累積 | 無持久記憶，無對話壓縮 | 🔴 高 |
| 5 | 智慧指令預測 | 無預測引擎，無情境建議 | 🟡 中 |
| 6 | 無頭模式與持續整合 | 有 `aa-gitpush` 但無完整 CI/CD 整合 | 🟡 中 |

---

## 二、階段 1：子代理系統與平行任務調度

### 現狀問題

AutoAgent-TW 的 `/aa-chain` 僅支援 `&&` / `||` / `|` 的線性管線，無法做到：
- 動態生成獨立子代理（Subagent）並行執行
- 主執行緒作為 Coordinator 進行任務拆解與結果綜合
- 子代理間的狀態隔離與結果回收

### 需新增模組

#### 1.1 `scripts/subagent/spawn_manager.py` — 子代理生成管理器

```python
# 核心概念：每個子代理是獨立的 Python 子進程，擁有自己的上下文與日誌
class SubagentSpawnManager:
    def spawn(self, task_spec: dict) -> str:
        """
        task_spec = {
            "role": "researcher" | "implementer" | "verifier",
            "prompt": "具體任務描述",
            "context_files": ["path/to/file.py"],
            "timeout": 300,
            "budget_tokens": 50000
        }
        回傳 subagent_id
        """

    def collect(self, subagent_id: str) -> dict:
        """等待子代理完成，回收結果 {status, output, logs, tokens_used}"""

    def parallel(self, task_specs: list[dict]) -> list[dict]:
        """批次生成多個子代理並行執行，全部完成後回傳結果列表"""
```

#### 1.2 `scripts/subagent/coordinator.py` — 任務協調器

```python
class Coordinator:
    """
    三階段管線：Research → Synthesis → Verification
    與 /aa-chain 不同，coordinator 具備動態任務拆解能力
    """

    def orchestrate(self, high_level_goal: str) -> dict:
        # Step 1: 將目標拆解為子任務（由 LLM 完成拆解）
        subtasks = self._decompose(high_level_goal)

        # Step 2: 平行派發研究型任務
        research_results = self.spawn_manager.parallel(
            [t for t in subtasks if t["type"] == "research"]
        )

        # Step 3: 主執行緒綜合規劃（依賴研究結果）
        plan = self._synthesize(research_results)

        # Step 4: 平行派發實作型任務
        impl_results = self.spawn_manager.parallel(
            [t for t in subtasks if t["type"] == "implement"]
        )

        # Step 5: 平行派發驗證型任務
        verify_results = self.spawn_manager.parallel(
            [t for t in subtasks if t["type"] == "verify"]
        )

        return {"plan": plan, "results": verify_results}
```

#### 1.3 新增指令 `/aa-orchestrate`

| 指令                                      | 功能                                                              |
| ----------------------------------------- | ----------------------------------------------------------------- |
| `/aa-orchestrate "實作使用者登入功能" ` | 自動拆解為研究現有 auth 模組、實作 OAuth 流程、撰寫測試三條平行線 |
| `/aa-orchestrate --resume <id>`         | 恢復中斷的協調任務                                                |
| `/aa-orchestrate --status`              | 查看所有子代理執行狀態                                            |

#### 1.4 修改現有檔案

- **`scripts/scheduler_daemon.py`**: 新增子代理生命週期管理，scheduler 需追蹤子進程 PID
- **`.agent-state/scheduled_tasks.json`**: schema 擴展，新增 `subagent_id` 欄位
- **`.agents/skills/status-notifier/templates/status.html`**: 儀表板新增子代理狀態面板（即時顯示各子代理進度條）

---

## 三、階段 2：MCP 協議整合層

### 現狀問題

AutoAgent-TW 完全沒有 MCP（Model Context Protocol）實作，所有外部工具整合都是硬編碼。對比 Claude Code 原生支援 MCP Server 的掛載能力，AutoAgent-TW 需要從零建立。

### 需新增模組

#### 2.1 `scripts/mcp/mcp_client.py` — MCP 客戶端核心

```python
import asyncio
import json
from typing import Any

class MCPClient:
    """
    支援 stdio / SSE 兩種傳輸模式的 MCP 客戶端
    連接到外部 MCP Server 後，將其工具註冊為 AutoAgent-TW 可調用的內部指令
    """

    def __init__(self, server_config: dict):
        self.server_config = server_config  # {name, transport, command, args, env}
        self.tools: dict[str, dict] = {}    # 已發現的遠端工具

    async def connect(self):
        """建立與 MCP Server 的連接（stdio pipe 或 SSE stream）"""

    async def list_tools(self) -> list[dict]:
        """向 MCP Server 查詢可用工具列表"""

    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """調用遠端 MCP 工具並回傳結果"""

    async def disconnect(self):
        """優雅關閉連接"""
```

#### 2.2 `scripts/mcp/registry.py` — MCP 工具註冊中心

```python
class MCPToolRegistry:
    """
    將所有已連接的 MCP Server 的工具統一註冊到 AutoAgent-TW 的指令系統中
    使得 /aa-chain 和 /aa-orchestrate 可以直接調用外部工具
    """

    def __init__(self):
        self.clients: dict[str, MCPClient] = {}
        self.tool_map: dict[str, str] = {}  # tool_name -> server_name

    def register_server(self, config: dict):
        """根據配置註冊一個 MCP Server"""

    def get_tool(self, tool_name: str) -> callable:
        """獲取已註冊工具的調用入口"""

    def list_all_tools(self) -> list[dict]:
        """列出所有可用的跨伺服器工具"""
```

#### 2.3 配置檔 `.agents/mcp_servers.json`

```json
{
  "servers": [
    {
      "name": "slack",
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-slack"],
      "env": { "SLACK_TOKEN": "${SLACK_BOT_TOKEN}" }
    },
    {
      "name": "linear",
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "mcp-server-linear"],
      "env": { "LINEAR_API_KEY": "${LINEAR_KEY}" }
    },
    {
      "name": "datadog",
      "transport": "sse",
      "url": "http://localhost:3001/sse",
      "env": { "DD_API_KEY": "${DATADOG_KEY}" }
    },
    {
      "name": "notion",
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-notion"],
      "env": { "NOTION_TOKEN": "${NOTION_KEY}" }
    },
    {
      "name": "postgres",
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-postgres"],
      "env": { "DATABASE_URL": "${DB_URL}" }
    }
  ]
}
```

#### 2.4 新增指令 `/aa-mcp`

| 指令                           | 功能                                 |
| ------------------------------ | ------------------------------------ |
| `/aa-mcp list`               | 列出所有已連接的 MCP Server 及其工具 |
| `/aa-mcp connect <server>`   | 手動連接指定 MCP Server              |
| `/aa-mcp test <tool> <args>` | 測試調用某個 MCP 工具                |
| `/aa-mcp logs`               | 查看 MCP 通訊日誌                    |

#### 2.5 修改現有檔案

- **`scripts/scheduler_daemon.py`**: 啟動時自動載入 `mcp_servers.json` 並初始化所有 MCP 連接
- **`_agents/workflows/aa-discuss.md`**: 工作流中可引用 MCP 工具，例如 `{{mcp:linear.get_issue}}`
- **`scripts/resilience/AA_Guardian.py`**: Guardian 可透過 MCP 接收外部告警（如 Datadog 事件）

---

## 四、階段 3：工作流客製化系統

### 現狀問題

AutoAgent-TW 的指令是硬編碼在主系統中的，團隊無法根據自身規範新增或修改工作流。Claude Code 的做法是透過 `CLAUDE.md` + 自訂 Skills + Hooks 三層機制實現完全客製化。

### 需新增模組

#### 4.1 `CLAUDE.md` 專案規範注入

建立專案根目錄的 `CLAUDE.md`，所有 AutoAgent-TW 實例啟動時自動載入：

```markdown
# CLAUDE.md — 專案規範（AutoAgent-TW 自動載入）

## 架構約束
- 所有 API 路由必須放在 `src/api/v{version}/` 下
- 資料庫遷移使用 Alembic，嚴禁直接修改 production schema
- 前端元件採用 Atomic Design（atoms → molecules → organisms）

## 程式碼風格
- Python: Black + Ruff，行寬 100
- TypeScript: ESLint + Prettier，使用 strict mode
- 命名：API 端點用 snake_case，前端元件用 PascalCase

## 測試要求
- 所有新功能必須包含單元測試（coverage ≥ 80%）
- API 端點必須有整合測試
- 禁止在 production code 中使用 `# type: ignore` 除非附帶解釋

## 禁止事項
- 不得引入 GPL 授權的依賴
- 不得在程式碼中硬編碼 secrets
- 不得使用 `any` type（TypeScript）
```

#### 4.2 `scripts/skills/skill_loader.py` — 自訂技能載入器

```python
class SkillLoader:
    """
    掃描 .agents/skills/ 下的 Markdown 指令檔，動態註冊為可用指令
    技能檔格式：
    ---
    name: commit
    trigger: /commit
    description: 規範式 Git Commit
    hooks: [pre-commit, post-commit]
    ---
    ## 執行步驟
    1. 執行 `git diff --staged` 取得暫存內容
    2. 根據 CLAUDE.md 的規範生成 commit message
    3. 執行 `git commit -m "<message>"`
    4. 觸發 post-commit hook
    """

    def discover_skills(self) -> list[dict]:
        """掃描 .agents/skills/ 目錄，解析所有 .md 技能檔"""

    def register_skill(self, skill_def: dict):
        """將技能註冊到指令系統"""

    def execute_skill(self, skill_name: str, args: dict) -> dict:
        """執行指定技能，回傳結果"""
```

#### 4.3 `scripts/hooks/hook_manager.py` — 生命週期鉤子管理器

```python
class HookManager:
    """
    綁定 AutoAgent-TW 生命週期事件，在特定時機自動執行腳本或技能
    """

    HOOK_EVENTS = [
        "PreToolUse",     # 在 AI 使用任何工具之前
        "PostToolUse",    # 在 AI 使用任何工具之後
        "PreCommit",      # 在 git commit 之前
        "PostCommit",     # 在 git commit 之後
        "PreDeploy",      # 在部署之前
        "OnTaskComplete", # 在任務完成時
        "OnBudgetExceed", # 在預算超標時
        "OnScheduleTick", # 在排程觸發時
    ]

    def register_hook(self, event: str, action: dict):
        """
        action = {
            "type": "command" | "skill" | "notify",
            "target": "npm run format" | "/verify" | "slack:#alerts",
            "condition": "file_ext == '.py'",  # 可選條件
            "timeout": 60
        }
        """

    def trigger(self, event: str, context: dict):
        """觸發指定事件的所有註冊鉤子"""
```

#### 4.4 配置檔 `.agents/hooks.json`

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "condition": "tool_name == 'write_file' && file_path.endsWith('.py')",
        "type": "command",
        "target": "ruff check --fix {file_path} && black {file_path}"
      }
    ],
    "PostToolUse": [
      {
        "condition": "tool_name == 'write_file' && file_path.endsWith('.ts')",
        "type": "command",
        "target": "npx eslint --fix {file_path}"
      }
    ],
    "PreCommit": [
      {
        "type": "skill",
        "target": "/verify"
      }
    ],
    "OnBudgetExceed": [
      {
        "type": "notify",
        "target": "slack:#dev-alerts"
      }
    ]
  }
}
```

#### 4.5 新增指令 `/aa-skill`

| 指令                              | 功能                         |
| --------------------------------- | ---------------------------- |
| `/aa-skill list`                | 列出所有已載入的自訂技能     |
| `/aa-skill create <name>`       | 互動式建立新技能檔           |
| `/aa-skill test <name>`         | 測試執行指定技能             |
| `/aa-hook list`                 | 列出所有已註冊的生命週期鉤子 |
| `/aa-hook add <event> <action>` | 新增鉤子                     |

#### 4.6 修改現有檔案

- **`scripts/scheduler_daemon.py`**: 啟動時呼叫 `SkillLoader.discover_skills()` 和 `HookManager.load_config()`
- **`README.md`**: 新增「自訂技能與鉤子」章節
- **`.agent-state/status_state.json`**: 新增 `active_skills` 和 `hook_triggers` 統計欄位

---

### 現狀問題

### 📚 `aa-memory` 指令完全使用指南 (AutoAgent-TW v1.9.0)

`aa-memory` 是專為 AutoAgent-TW 設計的持久化記憶管理工具。它允許您跨會話 (Session) 儲存架構決策、偏好設定或解決方案，並能靈活控制 AI 的專注力。

---

### 1. 基礎概念

記憶共分為三層 (`--level`)：

- **L1 (Session)**: 當前對話臨時記憶。
- **L2 (Project)**: **[預設]** 專案級持久記憶，儲存於 `.agent-state/memory/`。
- **L3 (Global)**: 跨專案通用記憶，儲存於使用者家目錄。

---

### 2. 常用操作指令

#### 📘 **列出項目 (List)**

顯示當前所有儲存的記憶、短 ID、標籤與建立時間。

```bash
python scripts/aa_memory.py list
```

> [!TIP]
> 帶有 `[FOCUSED]` 標籤的項目表示目前 AI **只會專注於此內容**。

#### 📝 **新增記憶 (Add)**

將重要的架構決策或 Bug 解決方案存入專案。

```bash
python scripts/aa_memory.py add "API 逾時設定應統一為 30 豪秒" --tags networking,config --level L2
```

#### 🎯 **專注模式 (Focus / Clear)**

當記憶過多且內容相互衝突時，讓 AI 只看特定的條目。

- **針對特定 ID 專注**:
  ```bash
  python scripts/aa_memory.py focus <ID末8碼>
  ```
- **解除專注 (恢復全部可見)**:
  ```bash
  python scripts/aa_memory.py focus clear
  ```

#### ❌ **刪除記憶 (Delete)**

永久移除過時或錯誤的上下文。

```bash
python scripts/aa_memory.py delete <ID末8碼>
```

#### 📤 **匯出上下文 (Export)**

預覽 AI 將會讀取到的記憶文字。

```bash
python scripts/aa_memory.py export
```

---

### 3. 進階參數速查表

| 參數        | 說明                             | 範例                       |
| :---------- | :------------------------------- | :------------------------- |
| `--level` | 指定記憶層級 (L1/L2/L3)          | `--level L3`             |
| `--tags`  | 為記憶加上標籤 (逗號分隔)        | `--tags database,v2,fix` |
| `id`      | 使用 `list` 指令輸出的 8 碼 ID | `d5386c74`               |

---

### 💡 實戰小技巧

1. **清理環境**：每當開始一個新子任務，建議先執行 `focus clear` 確保 AI 有完整的背景知識。
2. **解決衝突**：若 AI 重複犯錯（例如一直使用舊的 Library），請將正確的做法 `add` 進去，並對其執行 `focus`。

您可以現在輸入 `python scripts/aa_memory.py list` 來確認目前的記憶清單。

AutoAgent-TW 完全沒有持久化記憶機制。每次啟動都是從零開始，無法累積專案知識。Claude Code 的 auto-memory 功能能主動將架構決策和解決方案持久化。

### 需新增模組

#### 5.1 `scripts/memory/memory_store.py` — 記憶存儲引擎

```python
import json
import hashlib
from pathlib import Path
from datetime import datetime

class MemoryStore:
    """
    分層記憶系統：
    - L1 (Session): 當前對話的臨時記憶，存於 .agent-state/session_memory.json
    - L2 (Project): 專案級持久記憶，存於 .agent-state/project_memory.json
    - L3 (Global): 跨專案通用記憶，存於 ~/.autoagent/global_memory.json
    """

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.l1_path = self.project_root / ".agent-state" / "session_memory.json"
        self.l2_path = self.project_root / ".agent-state" / "project_memory.json"
        self.l3_path = Path.home() / ".autoagent" / "global_memory.json"

    def remember(self, content: str, level: str = "L2", tags: list[str] = None):
        """
        儲存一條記憶
        content: 記憶內容（架構決策、解法、偏好等）
        level: L1/L2/L3
        tags: 標籤，用於後續檢索（如 ["auth", "oauth", "decision"]）
        """

    def recall(self, query: str, level: str = None, top_k: int = 5) -> list[dict]:
        """
        根據查詢檢索相關記憶
        使用 embedding 相似度 + 標籤匹配的混合檢索
        """

    def compress_session(self):
        """
        對話過長時，自動將 L1 記憶摘要壓縮並提升為 L2
        保留關鍵決策，丟棄中間推理過程
        """

    def export_context(self) -> str:
        """
        為新會話生成上下文摘要，包含：
        - 最近的架構決策
        - 當前進行中的任務
        - 已知的問題與 workaround
        - 使用者偏好
        """
```

#### 5.2 `scripts/memory/context_compressor.py` — 對話上下文壓縮器

```python
class ContextCompressor:
    """
    當對話 token 數接近上下文視窗上限時，自動觸發壓縮
    Claude Code 的做法是將舊對話摘要為精簡版本，保留關鍵資訊
    """

    def __init__(self, max_tokens: int = 800000):
        self.max_tokens = max_tokens
        self.compression_threshold = 0.85  # 達到 85% 時觸發

    def should_compress(self, current_tokens: int) -> bool:
        """判斷是否需要壓縮"""

    def compress(self, conversation: list[dict]) -> list[dict]:
        """
        將舊對話壓縮為摘要
        保留：程式碼變更、決策記錄、錯誤修復
        丟棄：問候語、重複確認、中間推理
        回傳壓縮後的對話歷史
        """
```

#### 5.3 記憶檔案結構

```
.agent-state/
├── session_memory.json      # L1: 當前會話記憶
├── project_memory.json      # L2: 專案持久記憶
├── memory_index.faiss       # 向量索引（用於語意檢索）
└── context_compressions/    # 壓縮歷史
    ├── 2026-04-01T10-00.json
    └── 2026-04-02T14-30.json

~/.autoagent/
└── global_memory.json       # L3: 跨專案記憶
```

#### 5.4 新增指令 `/aa-memory`

| 指令                                       | 功能                                 |
| ------------------------------------------ | ------------------------------------ |
| `/aa-memory search <query>`              | 搜尋專案記憶                         |
| `/aa-memory add <content> --tags <tags>` | 手動新增記憶                         |
| `/aa-memory list`                        | 列出所有記憶條目                     |
| `/aa-memory compress`                    | 手動觸發對話壓縮                     |
| `/aa-memory export`                      | 匯出當前上下文摘要（用於新會話載入） |

#### 5.5 修改現有檔案

- **`scripts/scheduler_daemon.py`**: 啟動時呼叫 `memory_store.export_context()` 載入歷史記憶
- **`.agents/workflows/aa-discuss.md`**: 工作流開始前先查詢相關記憶
- **`scripts/resilience/budget_monitor.py`**: 預算接近上限時觸發 `compress_session()`
- **`.agents/skills/status-notifier/templates/status.html`**: 儀表板新增記憶統計面板（記憶條目數、壓縮次數、token 節省量）

---

## 六、階段 5：智慧指令預測引擎

### 現狀問題

AutoAgent-TW 是純被動系統，開發者需要明確輸入指令。Claude Code 會根據當前開發進度主動建議下一步操作。

### 需新增模組

#### 6.1 `scripts/predictor/command_predictor.py` — 指令預測引擎

```python
class CommandPredictor:
    """
    根據當前開發上下文，預測下一步最可能需要執行的指令
    類似 IDE 的 auto-complete，但作用於工作流層面
    """

    # 預測規則引擎（可由 LLM 增強）
    PREDICTION_RULES = {
        "file_saved_after_edit": {
            "suggestion": "run the tests",
            "command": "npm test",
            "confidence": 0.9
        },
        "all_tests_passed": {
            "suggestion": "commit this change",
            "command": "/commit",
            "confidence": 0.85
        },
        "ci_failed": {
            "suggestion": "fix the failing test",
            "command": "/aa-orchestrate 'fix CI failure'",
            "confidence": 0.95
        },
        "feature_implementation_complete": {
            "suggestion": "create a pull request",
            "command": "/aa-gitpush",
            "confidence": 0.8
        },
        "merge_conflict_detected": {
            "suggestion": "resolve merge conflicts",
            "command": "/aa-orchestrate 'resolve merge conflicts'",
            "confidence": 0.9
        },
    }

    def predict(self, context: dict) -> list[dict]:
        """
        context = {
            "last_action": "write_file",
            "files_changed": ["src/auth/login.py"],
            "git_status": "modified",
            "test_status": "unknown",
            "active_task": "implement user login"
        }
        回傳 [{suggestion, command, confidence, reason}, ...]
        """

    def render_suggestions(self, predictions: list[dict]) -> str:
        """渲染為終端機可顯示的建議列表"""
```

#### 6.2 `scripts/predictor/context_tracker.py` — 開發上下文追蹤器

```python
class ContextTracker:
    """
    持續追蹤開發者的操作序列，維護即時開發上下文
    作為 CommandPredictor 的輸入來源
    """

    def track_file_change(self, file_path: str, change_type: str):
        """記錄檔案變更"""

    def track_command(self, command: str, result: str):
        """記錄指令執行結果"""

    def track_git_event(self, event_type: str, details: dict):
        """記錄 Git 事件"""

    def get_current_context(self) -> dict:
        """取得當前開發上下文快照"""
```

#### 6.3 修改現有檔案

- **`scripts/scheduler_daemon.py`**: 整合 ContextTracker，每次工具調用後更新上下文
- **`scripts/hooks/hook_manager.py`**: PostToolUse 鉤子觸發後呼叫 `predictor.predict()`
- **`.agents/skills/status-notifier/templates/status.html`**: 儀表板顯示「建議下一步」面板

---

## 七、階段 6：無頭模式與 CI/CD 整合

### 現狀問題

AutoAgent-TW 有 `aa-gitpush` 但僅限於本地推送，缺乏完整的 CI/CD 整合能力。Claude Code 的無頭模式（Headless Mode）可以被 GitHub Actions 等系統呼叫，實現完全自動化的程式碼審查與修復。

### 需新增模組

#### 7.1 `scripts/headless/headless_runner.py` — 無頭模式執行器

```python
class HeadlessRunner:
    """
    非互動模式執行 AutoAgent-TW，可被腳本和 CI/CD 系統呼叫
    對應 Claude Code 的 `claude -p "prompt"` 模式
    """

    def run(self, prompt: str, options: dict = None) -> dict:
        """
        非互動執行：
        headless_runner.run(
            prompt="Review PR #42 and fix any issues",
            options={
                "repo": ".",
                "branch": "feature/login",
                "output_format": "json",
                "timeout": 600,
                "auto_push": True
            }
        )
        """

    def run_from_github_event(self, event_payload: dict) -> dict:
        """
        從 GitHub Webhook 事件觸發執行
        支援：issues, pull_request, push, issue_comment
        """
```

#### 7.2 `.github/workflows/aa-agent.yml` — GitHub Actions 整合

```yaml
name: AutoAgent-TW CI Agent

on:
  issue_comment:
    types: [created]
  pull_request:
    types: [opened, synchronize]

jobs:
  agent-review:
    if: |
      github.event_name == 'pull_request' ||
      (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude'))
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup AutoAgent-TW
        run: |
          pip install -r requirements.txt
          echo "${{ secrets.AUTOAGENT_CONFIG }}" > .agent-state/config.json

      - name: Run Agent
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python scripts/headless/headless_runner.py \
            --prompt "${{ github.event.comment.body || 'Review this PR' }}" \
            --context pr:${{ github.event.pull_request.number }} \
            --auto-push \
            --output-format github-comment

      - name: Post Results
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const results = require('./agent-results.json');
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: results.summary
            });
```

#### 7.3 `scripts/headless/github_integration.py` — GitHub 整合層

```python
class GitHubIntegration:
    """
    處理 GitHub API 互動：讀取 PR diff、發布 review comment、推送修復
    """

    def get_pr_context(self, pr_number: int) -> dict:
        """取得 PR 的 diff、檔案列表、評論"""

    def post_review(self, pr_number: int, review: dict):
        """發布程式碼審查評論"""

    def push_fix(self, branch: str, commit_message: str):
        """將修復推送到指定分支"""

    def create_check_run(self, name: str, status: str, output: dict):
        """建立 GitHub Check Run（顯示在 PR 頁面）"""
```

#### 7.4 新增指令 `/aa-headless`

| 指令                      | 功能                       |
| ------------------------- | -------------------------- |
| `/aa-headless test`     | 本地模擬無頭模式執行       |
| `/aa-headless setup-ci` | 生成 GitHub Actions 配置檔 |
| `/aa-headless status`   | 查看最近的 CI 觸發記錄     |

#### 7.5 修改現有檔案

- **`scripts/aa_git_pusher.py`**: 擴展支援 PR 模式（不只 push，還能建立 PR）
- **`scripts/scheduler_daemon.py`**: 新增 webhook 監聽模式（可選）
- **`README.md`**: 新增「CI/CD 整合」章節
- **`.planning/ROADMAP.md`**: 更新路線圖，標註 CI/CD 階段

---

## 八、完整指令表（v2.0）

| 指令                | 階段        | 功能描述                 |
| ------------------- | ----------- | ------------------------ |
| `/aa-auto-build`  | 基礎        | 啟動全自動開發模式       |
| `/aa-schedule`    | 基礎        | 管理定時排程任務         |
| `/aa-chain`       | 基礎        | 條件式任務鏈組合         |
| `/aa-progress`    | 基礎        | 查看開發進度             |
| `/aa-version`     | 基礎        | 查詢版本與變更日誌       |
| `/aa-gitpush`     | 基礎        | Git 推送與 PR 建立       |
| `/aa-orchestrate` | **1** | 子代理協調與平行任務調度 |
| `/aa-mcp`         | **2** | MCP 伺服器管理與工具調用 |
| `/aa-skill`       | **3** | 自訂技能管理             |
| `/aa-hook`        | **3** | 生命週期鉤子管理         |
| `/aa-memory`      | **4** | 專案記憶與上下文管理     |
| `/aa-predict`     | **5** | 查看智慧指令建議         |
| `/aa-headless`    | **6** | 無頭模式與 CI/CD 整合    |

---

## 九、實施路線圖

```
2026 Q2
├── v1.9.0: 階段 1 — 子代理系統
│   ├── spawn_manager.py
│   ├── coordinator.py
│   └── /aa-orchestrate 指令
│
├── v2.0.0: 階段 2 — MCP 整合
│   ├── mcp_client.py
│   ├── registry.py
│   └── /aa-mcp 指令
│
2026 Q3
├── v2.1.0: 階段 3 — 工作流客製化
│   ├── CLAUDE.md 注入機制
│   ├── skill_loader.py
│   ├── hook_manager.py
│   └── /aa-skill, /aa-hook 指令
│
├── v2.2.0: 階段 4 — 記憶系統
│   ├── memory_store.py
│   ├── context_compressor.py
│   └── /aa-memory 指令
│
2026 Q4
├── v2.3.0: 階段 5 — 指令預測
│   ├── command_predictor.py
│   ├── context_tracker.py
│   └── /aa-predict 指令
│
└── v2.4.0: 階段 6 — CI/CD 整合
    ├── headless_runner.py
    ├── github_integration.py
    ├── GitHub Actions 範本
    └── /aa-headless 指令
```

---

## 十、相依性與風險

### 新增 Python 依賴

```
# requirements.txt 新增
anthropic>=0.39.0          # Claude API（子代理調用）
mcp>=1.0.0                 # MCP 協議客戶端
faiss-cpu>=1.8.0           # 向量索引（記憶檢索）
pygithub>=2.4.0            # GitHub API 整合
watchdog>=4.0.0            # 檔案監控（上下文追蹤）
```

### 風險評估

| 風險                  | 等級  | 緩解措施                                                     |
| --------------------- | ----- | ------------------------------------------------------------ |
| 子代理 token 消耗失控 | 🔴 高 | 每個子代理強制設定 `budget_tokens`，由 budget_monitor 總控 |
| MCP Server 連接不穩定 | 🟡 中 | 實作自動重連 + 離線快取 + 斷路器模式                         |
| 記憶檔案損壞          | 🟡 中 | 定期備份 + WAL（Write-Ahead Log）模式                        |
| GitHub API 速率限制   | 🟡 中 | 實作請求隊列 + 指數退避重試                                  |
| 無頭模式安全漏洞      | 🔴 高 | 嚴格沙箱執行 + 最小權限原則 + 審計日誌                       |

---

## 附錄：與 Claude Code 功能對照

| Claude Code 功能    | AutoAgent-TW 對應模組            | 差異說明                                                    |
| ------------------- | -------------------------------- | ----------------------------------------------------------- |
| Subagents           | `subagent/`                    | Claude Code 內建；AutoAgent-TW 需自行實作進程管理           |
| MCP Support         | `mcp/`                         | Claude Code 原生支援；AutoAgent-TW 需從零建構客戶端         |
| CLAUDE.md           | 同名機制                         | 實現方式相同，但 AutoAgent-TW 需在 daemon 中注入            |
| Custom Skills       | `skills/skill_loader.py`       | Claude Code 用 `/command`；AutoAgent-TW 用 `/aa-skill`  |
| Hooks               | `hooks/hook_manager.py`        | 概念相同，AutoAgent-TW 的事件模型需與現有事件驅動整合       |
| Auto-memory         | `memory/`                      | Claude Code 內建；AutoAgent-TW 需實作分層存儲與壓縮         |
| Smart Predictions   | `predictor/`                   | Claude Code 內建；AutoAgent-TW 需規則引擎 + LLM 增強        |
| Headless Mode       | `headless/`                    | Claude Code CLI 參數；AutoAgent-TW 需 Python 入口 + CI 範本 |
| Context Compression | `memory/context_compressor.py` | 核心難點，需平衡壓縮率與資訊保留                            |

---

*本文件由 AutoAgent-TW 規劃系統生成，持續更新中。*

```

這份方案的核心設計原則是**漸進式增量**——每個階段都是獨立可交付的，前一階段的完成不阻塞後一階段的開發啟動。最關鍵的優先順序是 **階段 1（子代理）+ 階段 4（記憶）**，因為這兩者是其他所有階段的基礎能力支撐。
```

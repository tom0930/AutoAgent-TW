```markdown
# aa-testclaw.md

## AutoAgent-TW → TestClaw 自主代理改造方案

> 目標：將 AutoAgent-TW 從「自動化流水線」升級為具備自主規劃、動態工具調用、錯誤恢復與長期記憶的智能代理系統（TestClaw）。

---

## 一、現狀分析

### 1.1 AutoAgent-TW 當前架構

```

使用者指令 (/aa-auto-build)
        │
        ▼
┌─────────────────┐
│   Task Planner  │  ← 一次性 LLM 規劃
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Builder      │  ← 線性執行：寫碼 → 測試
└────────┬────────┘
         │ 失敗
         ▼
┌─────────────────┐
│  Self-Healer    │  ← 最多 3 輪重試
└────────┬────────┘
         │ 通過
         ▼
┌─────────────────┐
│   Guardian      │  ← 安全審查
└────────┬────────┘
         │
         ▼
      完成輸出

```

**限制：**
- 規劃為一次性靜態，無法中途調整
- 錯誤恢復僅限「重試」，無法搜索外部解決方案
- 無工具調用能力（不能搜網頁、查文件）
- 無長期記憶，跨會話狀態依賴簡單檔案
- 無主動探索能力，遇到未知問題即卡住

### 1.2 OpenClaw 式系統特徵

| 能力 | OpenClaw | AutoAgent-TW（現狀） |
|------|----------|---------------------|
| 目標分解 | 多層級動態規劃 | 一次性靜態規劃 |
| 工具調用 | 搜尋/瀏覽/執行/繪圖 | 僅執行內部命令 |
| 錯誤恢復 | 搜索+回退+詢問 | 最多3輪重試 |
| 記憶系統 | 向量DB + 結構化記憶 | 無/簡單檔案 |
| 自主探索 | 主動嘗試未知方案 | 依賴預設流程 |
| 反思機制 | 階段性自我評估 | 無 |

---

## 二、TestClaw 目標架構

### 2.1 整體架構圖

```

    ┌──────────────────────────┐
                    │     使用者自然語言指令      │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │    Orchestrator（編排器）   │
                    │  ┌────────────────────┐  │
                    │  │  核心代理循環 Loop   │  │
                    │  │  observe → think   │  │
                    │  │  → decide → act    │  │
                    │  │  → reflect → ...   │  │
                    │  └────────────────────┘  │
                    └───┬──────┬──────┬───────┘
                        │      │      │
            ┌───────────┘      │      └───────────┐
            ▼                  ▼                  ▼
   ┌─────────────┐   ┌──────────────┐   ┌──────────────┐
   │  工具註冊表   │   │  記憶管理器    │   │  安全沙箱     │
   │  Tool Registry│   │  Memory Mgr  │   │  Sandbox     │
   └──────┬──────┘   └──────┬───────┘   └──────┬───────┘
          │                 │                   │
    ┌─────┼─────┐     ┌────┼────┐         ┌────┼────┐
    ▼     ▼     ▼     ▼    ▼    ▼         ▼    ▼    ▼
  搜尋  執行  瀏覽  項目  對話  外部    命令  網路  檔案
  工具  命令  網頁  記憶  歷史  知識    白名單 代理  隔離

```

### 2.2 核心代理循環（Agent Loop）

```

┌─────────────────────────────────────────────────┐
│                  Agent Loop                      │
│                                                  │
│   ┌──────────┐                                   │
│   │ OBSERVE  │ 讀取：檔案系統、終端輸出、測試結果、 │
│   │          │ 專案狀態、對話歷史                  │
│   └────┬─────┘                                   │
│        ▼                                         │
│   ┌──────────┐                                   │
│   │  THINK   │ LLM 推理：分析現狀、評估進度、      │
│   │          │ 識別障礙、產生假設                  │
│   └────┬─────┘                                   │
│        ▼                                         │
│   ┌──────────┐                                   │
│   │  DECIDE  │ 選擇行動：寫碼/執行/搜尋/瀏覽/     │
│   │          │ 詢問人類/回退/繼續                  │
│   └────┬─────┘                                   │
│        ▼                                         │
│   ┌──────────┐                                   │
│   │   ACT    │ 在沙箱內執行選定的行動              │
│   └────┬─────┘                                   │
│        ▼                                         │
│   ┌──────────┐                                   │
│   │ REFLECT  │ 評估結果、更新記憶、判斷是否陷入    │
│   │          │ 循環、決定是否調整計劃              │
│   └────┬─────┘                                   │
│        │                                         │
│        ▼                                         │
│   目標達成？─── 否 ──→ 回到 OBSERVE               │
│        │                                         │
│       是                                         │
│        ▼                                         │
│     完成                                          │
└─────────────────────────────────────────────────┘

```

---

## 三、詳細修改方案

### 3.1 模組一：Orchestrator（編排器）

**檔案：** `src/orchestrator.py`（新建）

Orchestrator 是 TestClaw 的大腦，取代原有的線性流程。

```python
# src/orchestrator.py — 核心概念結構

class Orchestrator:
    """TestClaw 核心編排器，管理整個代理循環。"""

    def __init__(self, project_path: str, llm_client, config: dict):
        self.project_path = project_path
        self.llm = llm_client
        self.tool_registry = ToolRegistry()
        self.memory = MemoryManager(project_path)
        self.sandbox = Sandbox()
        self.max_iterations = config.get("max_iterations", 50)
        self.cost_budget = config.get("cost_budget_usd", 5.0)

    def run(self, user_goal: str) -> dict:
        """主入口：接收自然語言目標，啟動代理循環。"""

        # Step 0: 目標解析與任務分解
        plan = self._decompose_goal(user_goal)

        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1

            # OBSERVE
            observation = self._observe()

            # THINK
            thought = self._think(observation, plan)

            # 判斷是否完成
            if thought.get("goal_achieved"):
                return self._finalize()

            # 判斷是否陷入循環
            if self._is_stuck(thought):
                self._invoke_recovery()

            # DECIDE
            action = self._decide(thought)

            # ACT
            result = self._act(action)

            # REFLECT
            self._reflect(observation, action, result)
            plan = self._adjust_plan(plan, result)

        return {"status": "max_iterations_reached", "memory": self.memory.summary()}

    def _decompose_goal(self, goal: str) -> dict:
        """將模糊目標分解為多層級任務樹。"""
        prompt = f"""
        你是一個軟件工程規劃專家。請將以下目標分解為具體的任務樹：

        目標：{goal}
        專案路徑：{self.project_path}

        請以 JSON 格式輸出任務樹，每個節點包含：
        - id: 唯一標識
        - description: 任務描述
        - status: pending/in_progress/done/blocked
        - dependencies: 依賴的任務 ID
        - acceptance_criteria: 完成標準
        """
        return self.llm.structured_output(prompt)

    def _observe(self) -> dict:
        """收集當前環境的所有資訊。"""
        return {
            "file_tree": self._scan_project(),
            "recent_changes": self.memory.get_recent_changes(),
            "test_results": self.tool_registry.run_tool("run_tests"),
            "git_status": self.tool_registry.run_tool("git_status"),
            "errors": self._collect_errors(),
        }

    def _think(self, observation: dict, plan: dict) -> dict:
        """LLM 推理階段。"""
        prompt = f"""
        當前觀察：
        {json.dumps(observation, ensure_ascii=False, indent=2)}

        當前任務計劃：
        {json.dumps(plan, ensure_ascii=False, indent=2)}

        記憶摘要：
        {self.memory.get_summary()}

        請分析：
        1. 當前進度如何？
        2. 遇到了什麼障礙？
        3. 下一步應該做什麼？
        4. 是否需要改變計劃？
        5. 目標是否已達成？

        以 JSON 格式輸出你的思考過程。
        """
        return self.llm.structured_output(prompt)

    def _decide(self, thought: dict) -> dict:
        """根據思考結果決定具體行動。"""
        available_tools = self.tool_registry.list_tools()
        prompt = f"""
        基於以下思考：
        {json.dumps(thought, ensure_ascii=False, indent=2)}

        可用工具：
        {json.dumps(available_tools, ensure_ascii=False, indent=2)}

        請選擇一個具體行動，以 JSON 格式輸出：
        {{"tool": "tool_name", "params": {{...}}, "reasoning": "為什麼選擇這個行動"}}
        """
        return self.llm.structured_output(prompt)

    def _act(self, action: dict) -> dict:
        """在沙箱中執行行動。"""
        return self.sandbox.execute(
            tool_name=action["tool"],
            params=action["params"]
        )

    def _reflect(self, observation, action, result):
        """反思階段：更新記憶，評估是否陷入循環。"""
        self.memory.store_episode({
            "observation": observation,
            "action": action,
            "result": result,
            "timestamp": time.time(),
        })

    def _is_stuck(self, thought: dict) -> bool:
        """檢測是否陷入重複循環。"""
        recent_episodes = self.memory.get_recent_episodes(5)
        # 檢測連續相似行動
        actions = [ep["action"]["tool"] for ep in recent_episodes]
        if len(set(actions)) <= 1 and len(actions) >= 3:
            return True
        # 檢測連續失敗
        results = [ep["result"].get("success", False) for ep in recent_episodes]
        if not any(results) and len(results) >= 3:
            return True
        return False

    def _invoke_recovery(self):
        """多層級恢復策略。"""
        strategies = [
            self._recovery_web_search,      # 搜索解決方案
            self._recovery_rollback,         # 回退到上一可工作狀態
            self._recovery_alternative_path, # 嘗試替代實現路徑
            self._recovery_ask_human,        # 詢問使用者
        ]
        for strategy in strategies:
            if strategy():
                return True
        return False
```

**修改對應的現有檔案：**

- `src/commands/auto.py` — 將 `/aa-auto-build` 的入口改為呼叫 `Orchestrator.run()`
- `src/commands/resume.py` — 將 `/aa-resume` 改為從記憶中恢復並繼續代理循環

---

### 3.2 模組二：ToolRegistry（工具註冊表）

**檔案：** `src/tools/registry.py`（新建）

這是 TestClaw 與外部世界互動的介面。

```python
# src/tools/registry.py

class ToolRegistry:
    """管理所有可用工具的註冊與調度。"""

    def __init__(self):
        self._tools = {}
        self._register_default_tools()

    def _register_default_tools(self):
        """註冊預設工具集。"""

        # ──── 搜尋與瀏覽 ────
        self.register(Tool(
            name="web_search",
            description="使用網路搜尋引擎查詢資訊，適用於查詢技術文件、錯誤解決方案、API 文件。",
            parameters={
                "query": {"type": "string", "description": "搜尋關鍵字"},
                "num_results": {"type": "integer", "default": 5}
            },
            handler=self._web_search,
            cost=0.002,  # 預估每次調用成本
        ))

        self.register(Tool(
            name="browse_url",
            description="訪問指定 URL 並提取網頁內容。",
            parameters={
                "url": {"type": "string", "description": "目標網址"},
                "extract_mode": {"type": "string", "enum": ["text", "markdown", "html"], "default": "text"}
            },
            handler=self._browse_url,
            cost=0.003,
        ))

        # ──── 程式碼與執行 ────
        self.register(Tool(
            name="run_command",
            description="在沙箱中執行終端命令。",
            parameters={
                "command": {"type": "string", "description": "要執行的 shell 命令"},
                "timeout": {"type": "integer", "default": 30}
            },
            handler=self._run_command,
            cost=0.001,
            security_level="high",  # 需要沙箱保護
        ))

        self.register(Tool(
            name="run_tests",
            description="執行專案測試套件並返回結果。",
            parameters={
                "test_path": {"type": "string", "description": "測試路徑（可選，預設全部）"},
                "framework": {"type": "string", "description": "測試框架（自動偵測）"}
            },
            handler=self._run_tests,
            cost=0.001,
        ))

        # ──── 檔案操作 ────
        self.register(Tool(
            name="read_file",
            description="讀取指定檔案的內容。",
            parameters={
                "path": {"type": "string", "description": "檔案路徑（相對於專案根目錄）"},
                "start_line": {"type": "integer", "default": 0},
                "end_line": {"type": "integer", "default": -1}
            },
            handler=self._read_file,
            cost=0.0001,
        ))

        self.register(Tool(
            name="write_file",
            description="建立或覆寫檔案。",
            parameters={
                "path": {"type": "string", "description": "檔案路徑"},
                "content": {"type": "string", "description": "檔案內容"}
            },
            handler=self._write_file,
            cost=0.0001,
            security_level="medium",
        ))

        self.register(Tool(
            name="list_files",
            description="列出目錄結構。",
            parameters={
                "path": {"type": "string", "default": "."},
                "depth": {"type": "integer", "default": 3}
            },
            handler=self._list_files,
            cost=0.0001,
        ))

        # ──── Git 操作 ────
        self.register(Tool(
            name="git_status",
            description="查看 Git 狀態。",
            parameters={},
            handler=self._git_status,
            cost=0.0001,
        ))

        self.register(Tool(
            name="git_commit",
            description="提交當前變更。",
            parameters={
                "message": {"type": "string", "description": "提交訊息"}
            },
            handler=self._git_commit,
            cost=0.0001,
        ))

        self.register(Tool(
            name="git_rollback",
            description="回退到上一個提交。",
            parameters={
                "steps": {"type": "integer", "default": 1}
            },
            handler=self._git_rollback,
            cost=0.0001,
            security_level="high",
        ))

        # ──── 人類互動 ────
        self.register(Tool(
            name="ask_human",
            description="向使用者提問以獲取澄清或指示。僅在必要時使用。",
            parameters={
                "question": {"type": "string", "description": "要問使用者的問題"},
                "context": {"type": "string", "description": "問題的背景說明"},
                "options": {"type": "array", "items": {"type": "string"}, "description": "可選的選項（可選）"}
            },
            handler=self._ask_human,
            cost=0,
        ))

        # ──── 程式碼分析 ────
        self.register(Tool(
            name="search_code",
            description="在專案中搜尋程式碼（正則表達式或關鍵字）。",
            parameters={
                "pattern": {"type": "string", "description": "搜尋模式"},
                "file_filter": {"type": "string", "description": "檔案類型篩選（如 *.py）"}
            },
            handler=self._search_code,
            cost=0.0001,
        ))

    def register(self, tool: Tool):
        """註冊一個新工具。"""
        self._tools[tool.name] = tool

    def list_tools(self) -> list:
        """列出所有可用工具的描述（給 LLM 參考）。"""
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters,
            }
            for t in self._tools.values()
        ]

    def run_tool(self, name: str, **params) -> dict:
        """執行指定工具。"""
        tool = self._tools.get(name)
        if not tool:
            return {"success": False, "error": f"未知工具: {name}"}
        try:
            result = tool.handler(**params)
            return {"success": True, "output": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
```

**新增目錄結構：**

```
src/tools/
├── __init__.py
├── registry.py          # 工具註冊表
├── search.py            # web_search, browse_url 實現
├── executor.py          # run_command, run_tests 實現
├── filesystem.py        # read_file, write_file, list_files, search_code
├── git_tools.py         # git_status, git_commit, git_rollback
└── human.py             # ask_human 實現
```

---

### 3.3 模組三：MemoryManager（記憶管理器）

**檔案：** `src/memory/manager.py`（新建）

```python
# src/memory/manager.py

import json
import hashlib
from pathlib import Path
from datetime import datetime

class MemoryManager:
    """TestClaw 記憶管理器，負責儲存和檢索代理的各類記憶。"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.memory_dir = self.project_path / ".testclaw" / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # 記憶分區
        self.episodes = []        # 行動-結果序列（短期記憶）
        self.decisions = []       # 關鍵決策記錄
        self.errors = {}          # 錯誤及其解決方案
        self.plan_history = []    # 計劃變更歷史

        self._load_existing()

    def store_episode(self, episode: dict):
        """儲存一個觀察-行動-結果循環。"""
        episode["timestamp"] = datetime.now().isoformat()
        episode["id"] = hashlib.md5(
            json.dumps(episode, sort_keys=True).encode()
        ).hexdigest()[:8]
        self.episodes.append(episode)
        self._persist("episodes", self.episodes[-100:])  # 保留最近 100 條

    def store_solution(self, error_signature: str, solution: dict):
        """記住一個錯誤的解決方案（跨會話記憶）。"""
        self.errors[error_signature] = {
            "solution": solution,
            "timestamp": datetime.now().isoformat(),
            "success_count": self.errors.get(error_signature, {}).get("success_count", 0) + 1,
        }
        self._persist("errors", self.errors)

    def recall_solution(self, error_message: str) -> dict | None:
        """回憶：是否有類似錯誤的已知解決方案？"""
        for sig, record in self.errors.items():
            if sig in error_message or self._similarity(sig, error_message) > 0.7:
                return record["solution"]
        return None

    def get_recent_episodes(self, n: int = 5) -> list:
        return self.episodes[-n:]

    def get_recent_changes(self) -> list:
        """獲取最近的程式碼變更摘要。"""
        recent = self.episodes[-10:]
        changes = []
        for ep in recent:
            if ep.get("action", {}).get("tool") in ("write_file", "run_command"):
                changes.append({
                    "action": ep["action"],
                    "success": ep.get("result", {}).get("success", False),
                })
        return changes

    def get_summary(self) -> str:
        """生成記憶摘要（供 LLM 參考，控制 token 消耗）。"""
        return json.dumps({
            "total_episodes": len(self.episodes),
            "recent_actions": [
                ep["action"].get("tool") for ep in self.episodes[-5:]
            ],
            "known_errors": list(self.errors.keys()),
            "last_success": self._last_successful_action(),
        }, ensure_ascii=False)

    def _last_successful_action(self) -> dict | None:
        for ep in reversed(self.episodes):
            if ep.get("result", {}).get("success"):
                return {"tool": ep["action"].get("tool"), "time": ep["timestamp"]}
        return None

    def _persist(self, key: str, data):
        """持久化到磁碟。"""
        path = self.memory_dir / f"{key}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_existing(self):
        """從磁碟載入已有記憶。"""
        for key in ("episodes", "errors"):
            path = self.memory_dir / f"{key}.json"
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    setattr(self, key, json.load(f))

    def _similarity(self, a: str, b: str) -> float:
        """簡單字串相似度（後續可替換為向量相似度）。"""
        set_a = set(a.lower().split())
        set_b = set(b.lower().split())
        if not set_a or not set_b:
            return 0.0
        return len(set_a & set_b) / len(set_a | set_b)
```

**未來升級路徑：** 可將 `_similarity` 替換為向量資料庫（如 ChromaDB、FAISS），實現語義級別的記憶檢索。

---

### 3.4 模組四：Sandbox（安全沙箱）

**檔案：** `src/sandbox/manager.py`（新建）

```python
# src/sandbox/manager.py

import subprocess
import tempfile
import shutil
from pathlib import Path

class Sandbox:
    """安全執行環境，隔離所有代理操作。"""

    def __init__(self, project_path: str, config: dict = None):
        self.project_path = Path(project_path)
        self.config = config or {}

        # 安全白名單
        self.allowed_commands = self.config.get("allowed_commands", [
            "python", "pip", "node", "npm", "npx", "yarn",
            "git", "pytest", "jest", "cargo", "go",
            "ls", "cat", "head", "tail", "grep", "find", "wc",
            "mkdir", "touch", "cp", "mv",
        ])

        self.blocked_commands = [
            "rm -rf /", "sudo", "chmod 777",
            "curl | bash", "wget | bash",
            ":(){ :|:& };:",  # fork bomb
        ]

        self.blocked_domains = self.config.get("blocked_domains", [])

        self.max_output_size = 1024 * 100  # 100KB
        self.default_timeout = 30  # 秒

    def execute(self, tool_name: str, params: dict) -> dict:
        """根據工具類型分派到對應的沙箱執行方法。"""
        handlers = {
            "run_command": self._exec_command,
            "run_tests": self._exec_tests,
            "write_file": self._exec_write_file,
            "read_file": self._exec_read_file,
            "list_files": self._exec_list_files,
            "search_code": self._exec_search_code,
            "web_search": self._exec_web_search,
            "browse_url": self._exec_browse_url,
            "git_status": self._exec_git_status,
            "git_commit": self._exec_git_commit,
            "git_rollback": self._exec_git_rollback,
        }
        handler = handlers.get(tool_name)
        if not handler:
            return {"success": False, "error": f"沙箱不支援工具: {tool_name}"}
        return handler(params)

    def _exec_command(self, params: dict) -> dict:
        """在沙箱中執行 shell 命令。"""
        command = params.get("command", "")
        timeout = params.get("timeout", self.default_timeout)

        # 安全檢查
        if not self._is_command_allowed(command):
            return {
                "success": False,
                "error": f"命令被安全策略阻止: {command[:50]}...",
                "blocked_reason": "不在白名單中或匹配黑名單規則"
            }

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            output = result.stdout + result.stderr
            # 截斷過長輸出
            if len(output) > self.max_output_size:
                output = output[:self.max_output_size] + "\n... (輸出被截斷)"

            return {
                "success": result.returncode == 0,
                "exit_code": result.returncode,
                "stdout": result.stdout[:self.max_output_size],
                "stderr": result.stderr[:self.max_output_size],
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"命令超時 ({timeout}秒)"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _exec_write_file(self, params: dict) -> dict:
        """安全地寫入檔案。"""
        path = self.project_path / params["path"]

        # 安全檢查：防止路徑穿越
        try:
            path.resolve().relative_to(self.project_path.resolve())
        except ValueError:
            return {"success": False, "error": "路徑穿越被阻止"}

        # 禁止寫入敏感檔案
        forbidden = [".env", ".git/config", "id_rsa", ".ssh/"]
        if any(str(path).endswith(f) or f in str(path) for f in forbidden):
            return {"success": False, "error": "禁止寫入敏感檔案"}

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(params["content"])
            return {"success": True, "output": f"檔案已寫入: {params['path']}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _is_command_allowed(self, command: str) -> bool:
        """檢查命令是否在白名單中。"""
        # 檢查黑名單
        for blocked in self.blocked_commands:
            if blocked in command:
                return False

        # 檢查白名單（命令的第一個詞）
        cmd_base = command.strip().split()[0] if command.strip() else ""
        return cmd_base in self.allowed_commands
```

---

### 3.5 模組五：恢復策略系統

**檔案：** `src/recovery/strategies.py`（新建）

```python
# src/recovery/strategies.py

class RecoveryManager:
    """多層級錯誤恢復策略管理器。"""

    def __init__(self, orchestrator):
        self.orch = orchestrator
        self.strategies = [
            (self.strategy_web_search,    "搜索網路解決方案", 1),
            (self.strategy_rollback,      "Git 回退",        2),
            (self.strategy_alternative,   "嘗試替代方案",    3),
            (self.strategy_ask_human,     "詢問使用者",      4),
        ]

    def recover(self, error_context: dict) -> bool:
        """依序嘗試恢復策略。"""
        # 先檢查記憶中是否有已知解決方案
        known = self.orch.memory.recall_solution(error_context.get("error_message", ""))
        if known:
            self.orch.log("從記憶中找到已知解決方案，直接套用")
            return self._apply_solution(known)

        # 依優先級嘗試策略
        for strategy_fn, name, priority in self.strategies:
            self.orch.log(f"嘗試恢復策略 [{priority}]: {name}")
            if strategy_fn(error_context):
                self.orch.log(f"恢復策略 [{name}] 成功")
                # 記住成功的解決方案
                self.orch.memory.store_solution(
                    error_context.get("error_signature", ""),
                    {"strategy": name, "context": error_context}
                )
                return True
        return False

    def strategy_web_search(self, context: dict) -> bool:
        """策略 1：搜索網路找解決方案。"""
        error = context.get("error_message", "")
        tech_stack = context.get("tech_stack", "")

        # 構建搜尋查詢
        query = f"{tech_stack} {error} solution"
        result = self.orch.tool_registry.run_tool("web_search", query=query)

        if result["success"] and result["output"]:
            # 讓 LLM 分析搜尋結果並產生解決方案
            solution = self.orch.llm.reason(
                f"根據以下搜尋結果，為錯誤 '{error}' 產生解決方案：\n"
                f"{result['output']}"
            )
            if solution.get("action"):
                self.orch._act(solution["action"])
                return True
        return False

    def strategy_rollback(self, context: dict) -> bool:
        """策略 2：回退到上一個可工作狀態。"""
        result = self.orch.tool_registry.run_tool("git_rollback", steps=1)
        if result["success"]:
            self.orch.log("已回退到上一個提交，重新嘗試")
            return True
        return False

    def strategy_alternative(self, context: dict) -> bool:
        """策略 3：讓 LLM 想出完全不同的實現方式。"""
        prompt = f"""
        當前實現方式失敗了。請想出一個完全不同的替代方案。

        失敗的任務：{context.get('task_description', '')}
        錯誤訊息：{context.get('error_message', '')}
        已嘗試的方法：{context.get('attempted_methods', [])}

        請提出一個使用不同技術/方法/架構的替代實現方案。
        """
        alternative = self.orch.llm.reason(prompt)
        if alternative.get("plan"):
            return True  # 更新計劃
        return False

    def strategy_ask_human(self, context: dict) -> bool:
        """策略 4：詢問使用者。"""
        result = self.orch.tool_registry.run_tool(
            "ask_human",
            question=f"我遇到了無法自動解決的問題：{context.get('error_message', '')}",
            context=context.get("task_description", ""),
            options=["跳過此功能", "嘗試不同的方法", "提供指導", "中止任務"]
        )
        if result["success"]:
            user_response = result["output"]
            if "跳過" in user_response:
                return True  # 標記為跳過
            elif "中止" in user_response:
                raise UserAbortException("使用者要求中止任務")
            # 其他回應會在下一輪循環中被考慮
            return False
        return False
```

---

### 3.6 模組六：LLM 推理層

**檔案：** `src/llm/reasoner.py`（新建）

```python
# src/llm/reasoner.py

class Reasoner:
    """LLM 推理層，封裝所有與 LLM 的交互。"""

    def __init__(self, api_key: str, model: str = "gpt-4o", max_tokens: int = 4096):
        self.client = OpenAI(api_key=api_key)  # 或其他 LLM 客戶端
        self.model = model
        self.max_tokens = max_tokens
        self.total_cost = 0.0
        self.cost_limit = 5.0  # USD

    def reason(self, prompt: str, system_prompt: str = None) -> dict:
        """通用推理方法。"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=0.1,  # 低溫度以獲得更穩定的輸出
            response_format={"type": "json_object"},  # 強制 JSON 輸出
        )

        self._track_cost(response.usage)
        return json.loads(response.choices[0].message.content)

    def structured_output(self, prompt: str) -> dict:
        """要求結構化 JSON 輸出。"""
        system = """
        你是一個嚴謹的軟件工程代理。你必須始終以有效的 JSON 格式回應。
        不要包含任何 JSON 以外的文字。
        """
        return self.reason(prompt, system_prompt=system)

    def _track_cost(self, usage):
        """追蹤 token 使用量和成本。"""
        # GPT-4o 定價（示例）
        input_cost = usage.prompt_tokens * 2.5 / 1_000_000
        output_cost = usage.completion_tokens * 10.0 / 1_000_000
        self.total_cost += input_cost + output_cost

        if self.total_cost > self.cost_limit:
            raise CostLimitExceeded(f"已達成本上限 ${self.cost_limit}")
```

---

## 四、目錄結構總覽

```
AutoAgent-TW/
├── src/
│   ├── orchestrator.py          # ★ 新增：核心編排器
│   ├── commands/
│   │   ├── auto.py              # 修改：改為呼叫 Orchestrator
│   │   ├── resume.py            # 修改：從記憶恢復
│   │   ├── testclaw.py          # ★ 新增：/aa-testclaw 指令
│   │   └── ...
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── registry.py          # ★ 新增：工具註冊表
│   │   ├── search.py            # ★ 新增：web_search, browse_url
│   │   ├── executor.py          # ★ 新增：run_command, run_tests
│   │   ├── filesystem.py        # ★ 新增：檔案操作工具
│   │   ├── git_tools.py         # ★ 新增：Git 工具
│   │   └── human.py             # ★ 新增：ask_human
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── manager.py           # ★ 新增：記憶管理器
│   │   └── vector_store.py      # 遠期：向量資料庫介面
│   ├── sandbox/
│   │   ├── __init__.py
│   │   └── manager.py           # ★ 新增：安全沙箱
│   ├── recovery/
│   │   ├── __init__.py
│   │   └── strategies.py        # ★ 新增：恢復策略
│   ├── llm/
│   │   ├── __init__.py
│   │   └── reasoner.py          # ★ 新增：LLM 推理層
│   └── ...                      # 現有檔案
├── .testclaw/
│   ├── memory/                  # 持久化記憶儲存
│   │   ├── episodes.json
│   │   └── errors.json
│   ├── config.yaml              # TestClaw 配置
│   └── sandbox/                 # 沙箱工作目錄
├── aa-testclaw.md               # ★ 本文件
└── ...
```

---

## 五、配置檔設計

**檔案：** `.testclaw/config.yaml`

```yaml
# TestClaw 配置檔

orchestrator:
  max_iterations: 50          # 最大代理循環次數
  idle_timeout: 300           # 無進展超時（秒）
  auto_commit: true           # 每個里程碑自動 git commit

llm:
  provider: "openai"          # openai / anthropic / local
  model: "gpt-4o"
  api_key_env: "OPENAI_API_KEY"  # 從環境變數讀取
  max_tokens: 4096
  cost_limit_usd: 5.0         # 單次任務成本上限
  temperature: 0.1

sandbox:
  enabled: true
  allowed_commands:
    - python
    - pip
    - node
    - npm
    - npx
    - git
    - pytest
    - jest
    - ls
    - cat
    - head
    - tail
    - grep
    - find
    - mkdir
    - touch
    - cp
    - mv
  blocked_domains: []
  max_output_kb: 100
  default_timeout_sec: 30

tools:
  web_search:
    provider: "duckduckgo"    # duckduckgo / google / brave
    max_results: 5
  browse_url:
    timeout: 15
    max_content_kb: 50

memory:
  backend: "json"             # json / chromadb / faiss
  max_episodes: 100           # 短期記憶上限
  persist: true

recovery:
  strategies:
    - web_search
    - rollback
    - alternative
    - ask_human
  max_recovery_attempts: 3

logging:
  level: "INFO"               # DEBUG / INFO / WARNING
  log_to_file: true
  log_dir: ".testclaw/logs"
```

---

## 六、Discord Bot 指令設計

### 6.1 新指令

| 指令                        | 說明                             |
| --------------------------- | -------------------------------- |
| `/aa-testclaw <目標描述>` | 啟動 TestClaw 自主代理執行任務   |
| `/aa-testclaw-status`     | 查看當前代理循環狀態、進度、成本 |
| `/aa-testclaw-pause`      | 暫停代理循環                     |
| `/aa-testclaw-resume`     | 恢復暫停的代理循環               |
| `/aa-testclaw-memory`     | 查看記憶摘要                     |
| `/aa-testclaw-tools`      | 列出可用工具                     |
| `/aa-testclaw-config`     | 查看/修改配置                    |

### 6.2 互動範例

```
使用者: /aa-testclaw 為我建立一個帶用戶登入的 Flask 待辦事項應用

TestClaw:
🎯 目標：建立帶用戶登入的 Flask 待辦事項應用
📋 計劃已生成（5 個階段）：
  1. ✅ 初始化 Flask 專案結構
  2. 🔄 實現用戶認證系統
  3. ⬜ 建立待辦事項 CRUD
  4. ⬜ 前端模板
  5. ⬜ 測試與驗證

🔍 [觀察] 專案目錄為空
💭 [思考] 需要先初始化 Flask 專案結構
⚡ [行動] 執行 `pip install flask flask-login flask-sqlalchemy`
  → ✅ 依賴安裝成功
⚡ [行動] 建立專案結構檔案...
  → ✅ app.py, models.py, templates/ 已建立

⏳ 進行中... (迭代 3/50 | 成本 $0.02)
```

---

## 七、實施階段規劃

### Phase 1：基礎架構（預計 1-2 週）

**目標：** 建立核心骨架，實現最小可行循環。

- [ ] 建立 `Orchestrator` 基本框架
- [ ] 建立 `ToolRegistry` 並註冊核心工具（read_file, write_file, run_command）
- [ ] 建立 `Sandbox` 基本安全檢查
- [ ] 建立 `Reasoner` LLM 推理層
- [ ] 實現 `/aa-testclaw` 指令入口
- [ ] **里程碑：** 代理能執行「讀取檔案 → 修改 → 測試」的簡單循環

### Phase 2：工具擴展（預計 1 週）

**目標：** 豐富工具集，讓代理能與外部世界互動。

- [ ] 實現 `web_search`（使用 DuckDuckGo API）
- [ ] 實現 `browse_url`（網頁內容提取）
- [ ] 實現 `search_code`（專案內程式碼搜尋）
- [ ] 實現 `ask_human`（Discord 互動詢問）
- [ ] 整合 Git 工具（status, commit, rollback）
- [ ] **里程碑：** 代理遇到未知錯誤時能自主搜尋解決方案

### Phase 3：記憶系統（預計 1 週）

**目標：** 讓代理具備學習和跨會話記憶能力。

- [ ] 實現 `MemoryManager` 基本功能
- [ ] 實現錯誤-解決方案配對記憶
- [ ] 實現計劃變更歷史記錄
- [ ] 實現 `/aa-testclaw-memory` 指令
- [ ] **里程碑：** 代理第二次遇到相同錯誤時能直接套用已知解決方案

### Phase 4：恢復策略（預計 1 週）

**目標：** 實現多層級錯誤恢復。

- [ ] 實現 `RecoveryManager` 及四種策略
- [ ] 實現陷入循環檢測
- [ ] 實現成本監控與預算控制
- [ ] 實現 `/aa-testclaw-status` 即時狀態查詢
- [ ] **里程碑：** 代理能從多種類型的錯誤中自主恢復

### Phase 5：優化與穩定（預計 1-2 週）

**目標：** 提升可靠性、降低成本、改善使用者體驗。

- [ ] 優化提示詞工程（減少 token 消耗）
- [ ] 增加階段性檢查點（checkpoint）
- [ ] 改善日誌與可觀測性
- [ ] 壓力測試與邊界案例處理
- [ ] 文件撰寫
- [ ] **里程碑：** TestClaw 可靠執行中等複雜度任務

### Phase 6：進階功能（遠期）

- [ ] 向量資料庫記憶（ChromaDB）
- [ ] 多代理協作（Builder + Reviewer 同時工作）
- [ ] 自訂工具註冊（使用者定義新工具）
- [ ] 視覺化代理思維過程
- [ ] 持續學習（從使用者反饋中改進）

---

## 八、安全考量

### 8.1 威脅模型

| 威脅                 | 風險等級 | 緩解措施                    |
| -------------------- | -------- | --------------------------- |
| 代理執行惡意命令     | 🔴 高    | 命令白名單 + 沙箱隔離       |
| 路徑穿越攻擊         | 🔴 高    | 路徑正規化 + 相對路徑限制   |
| 敏感檔案洩露         | 🔴 高    | 黑名單檔案 + 寫入保護       |
| 成本失控             | 🟡 中    | 預算上限 + 迭代限制         |
| 無限循環             | 🟡 中    | 迭代上限 + 陷入檢測         |
| 網路存取濫用         | 🟡 中    | 域名黑名單 + 流量限制       |
| LLM 幻覺導致錯誤操作 | 🟡 中    | 關鍵操作前確認 + Git 檢查點 |

### 8.2 安全原則

1. **最小權限**：代理只能執行白名單內的操作
2. **沙箱隔離**：所有命令在受控環境中執行
3. **可審計**：所有行動記錄到日誌，可事後審查
4. **可中斷**：使用者可隨時暫停或終止代理
5. **可回退**：每個里程碑自動建立 Git 檢查點
6. **成本控制**：硬性成本上限，超限自動停止

---

## 九、與現有架構的相容性

### 9.1 向後相容

- `/aa-auto-build` 保留原有功能，內部可選呼叫 Orchestrator
- `/aa-resume` 改為從 TestClaw 記憶中恢復
- Builder / QA / Guardian 模組可作為工具被 Orchestrator 調用
- 現有配置檔格式不變，TestClaw 配置獨立在 `.testclaw/config.yaml`

### 9.2 漸進式遷移

```
階段 1: 共存
  - /aa-auto-build → 使用舊流程
  - /aa-testclaw   → 使用新 Orchestrator

階段 2: 整合
  - /aa-auto-build 內部改為呼叫 Orchestrator（簡化模式）
  - /aa-testclaw   完整自主模式

階段 3: 統一
  - /aa-auto-build 為 /aa-testclaw 的別名
  - 所有功能統一到 Orchestrator 架構
```

---

## 十、總結

TestClaw 的核心理念是：

> **從「告訴機器怎麼做」轉變為「告訴機器做什麼」。**

通過引入 Orchestrator（編排器）、ToolRegistry（工具註冊表）、MemoryManager（記憶管理器）和 RecoveryManager（恢復管理器）四大核心模組，AutoAgent-TW 將從一個自動化流水線升級為具備自主規劃、動態工具調用、錯誤恢復與持續學習能力的智能代理系統。

這不是一個「全部重寫」的過程，而是一個 **漸進式演進**——從最小可行的代理循環開始，逐步擴展能力，最終實現高度自主的軟件工程代理。

---

*文件版本：v0.1*
*最後更新：2026-03-30*
*狀態：提案階段*

```

```

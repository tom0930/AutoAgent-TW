這份 Phase 169 藍圖已具備清晰的工程輪廓，特別是在 DAG 排序與 FileLock 的選型上符合「Simplicity Check」。為確保生產環境的穩定性、可追溯性與自動化收斂率，以下提供 **5 項關鍵優化** 與 **升級版實作架構**，直接補齊執行階段的技術債與潛在風險。

---

### 🔹 一、 5 項關鍵優化建議 (Better Plan)

| 優化維度                                      | 現況痛點                                                  | 優化方案                                                                                                                                                                                                           | 預期效益                                   |
| :-------------------------------------------- | :-------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------- |
| **1. 共識到 DAG 的自動映射**            | `ConsensusResult` 缺乏標準化結構轉為執行節點            | 定義 `ExecutionNode` Schema，自動解析 Phase 168 的 `dependencies` 與 `adopted_decision`，使用 `topological_sort` 生成執行隊列。若偵測循環依賴，自動降級為 `Sequential Fallback`。                        | 消除人工編排，確保依賴圖 100% 可計算       |
| **2. 邏輯鎖 + Git 原子提交**            | 純記憶體 FileLock 崩潰即失效，且無法處理語義衝突          | 採用**Orchestrator 邏輯鎖 (排程用)** + **Git Index 暫存 (物理用)**。每個 Agent 完成後自動 `git add` 至暫存區，不直接 `commit`。全部完成或達閾值後觸發 `Validation Gate`，通過才統一 `commit`。 | 避免檔案損壞，支援失敗回滾與審計           |
| **3. 上下文動態分片 (Context Scoping)** | 共享 Workspace 易導致 Token 膨脹與資訊越權                | 實作 `ContextScopeRouter`，依任務類型動態過濾 `allowed_paths` 與 `read_limit`。例如 UI Agent 僅載入 `src/components/`，Security Agent 僅載入 `config/` 與依賴樹。                                        | 降低 40%+ Token 消耗，符合 STRIDE 最小權限 |
| **4. 執行驗證門 (Validation Gate)**     | 依賴圖正確 ≠ 語義相容（如 API 簽名變更導致前端編譯失敗） | 在 DAG 尾端插入 `Pre-Merge Validator` 節點。自動執行 `lint + typecheck + unit_test`。若失敗，提取 `diff` 與 `error_log` 觸發 `Reflection Loop` 回傳對應 Agent。                                          | 攔截 90%+ 語義衝突，避免無效 Commit        |
| **5. 嚴格 TTL 與狀態復原**              | `asyncio.wait_for` 僅中止任務，未清理 Workspace         | 封裝 `Executor` 為 `contextmanager`。超時或異常時自動：① 釋放邏輯鎖 ② 回滾 Git Index (`git reset`) ③ 清除暫存檔 ④ 記錄 `audit.log`。確保系統始終處於乾淨狀態。                                         | 符合 Strict TTL DoD，永不留殘留狀態        |

---

### 🔹 二、 升級版執行工作流 (Execution Pipeline)

```text
[Phase 168 ConsensusResult 輸入]
        ↓
1. DAG Builder → 解析 dependencies, 生成 ExecutionNode[]
   ├─ 偵測循環 → 降級 Sequential
   └─ 計算 Critical Path → 預估執行時間
        ↓
2. ContextScopeRouter → 依角色動態載入 Context Snippets
   ├─ 注入 allowed_paths, read_limits
   └─ 屏蔽未授權目錄與環境變數
        ↓
3. DAG Executor (asyncio.TaskGroup + Logical Locks)
   ├─ 依拓撲排序發射任務
   ├─ 衝突檢測：若多 Agent 觸及同一路徑 → 自動序列化為子圖
   ├─ 嚴格 TTL：逾時強制 cancel + workspace rollback
   └─ 完成即 git add (暫存，不 commit)
        ↓
4. Validation Gate → Lint / TypeCheck / Test
   ├─ 通過 → git commit -m "Auto-exec: [Phase 169] <summary>"
   └─ 失敗 → 提取 diff + error_log → 觸發 Reflection Loop (max 2)
        ↓
5. CLI Live 渲染 → 即時顯示拓撲進度、鎖狀態、Diff 預覽、TTL 倒數
```

---

### 🔹 三、 核心實作骨架提示 (`executor.py`, `dag.py`, `lock_manager.py`)

#### 1. `dag.py` (依賴解析與拓撲排序)

```python
from typing import List, Dict, Set
from graphlib import TopologicalSorter

class ExecutionNode:
    def __init__(self, id: str, role: str, files: List[str], depends_on: List[str]):
        self.id = id
        self.role = role
        self.files = files
        self.depends_on = depends_on

def build_dag(consensus_result: Dict) -> List[ExecutionNode]:
    nodes = []
    for task in consensus_result["tasks"]:
        nodes.append(ExecutionNode(
            id=task["id"],
            role=task["role"],
            files=task["target_files"],
            depends_on=task.get("dependencies", [])
        ))
    # 驗證循環依賴
    graph = {n.id: n.depends_on for n in nodes}
    ts = TopologicalSorter(graph)
    ts.prepare()
    return list(ts.static_order()) # 若循環則拋出 CycleError
```

#### 2. `lock_manager.py` (邏輯鎖 + 衝突降級)

```python
import asyncio
from collections import defaultdict

class FileLockManager:
    def __init__(self):
        self._locks = defaultdict(asyncio.Lock)
        self._active_writers = set()

    async def acquire(self, file_path: str, task_id: str):
        lock = self._locks[file_path]
        await lock.acquire()
        self._active_writers.add((task_id, file_path))

    async def release(self, file_path: str, task_id: str):
        self._locks[file_path].release()
        self._active_writers.discard((task_id, file_path))

    def detect_conflict(self, files_a: List[str], files_b: List[str]) -> bool:
        return bool(set(files_a) & set(files_b))
```

#### 3. `executor.py` (核心分派與 TTL 封裝)

```python
import asyncio
from contextlib import asynccontextmanager
import subprocess

@asynccontextmanager
async def isolated_executor(task: ExecutionNode, ttl: int = 300):
    # 1. Context Scoping & Lock Acquisition
    scope = ContextScopeRouter.get_scope(task.role, task.files)
    # ... (acquire locks, prepare env) ...
  
    try:
        # 2. 執行代理任務
        result = await asyncio.wait_for(
            agent_client.execute(task, scope), timeout=ttl
        )
        # 3. Git 暫存 (不 commit)
        subprocess.run(["git", "add"] + task.files, check=True)
        yield result
    except asyncio.TimeoutError:
        # 4. Rollback & Cleanup
        subprocess.run(["git", "reset", "--", *task.files], check=True)
        raise RuntimeError(f"[{task.id}] TTL exceeded. Rolled back.")
    finally:
        # 5. 釋放邏輯鎖
        for f in task.files:
            await lock_manager.release(f, task.id)
```

---

### 🔹 四、 強化版 STRIDE 與 DoD 對照清單

| 威脅/需求                          | Phase 169 實作對應                                                               | 狀態   |
| :--------------------------------- | :------------------------------------------------------------------------------- | :----- |
| ✅**Spoofing**               | `TaskDispatcher` 驗證 `Agent Identity Token` + 角色白名單路由                | 已強化 |
| ✅**Tampering**              | `FileLockManager` 邏輯互斥 + `git reset` 物理回滾                            | 已強化 |
| ✅**Repudiation**            | `execution_audit.log` 記錄 `task_id, diff_hash, exit_code, token_used`       | 已強化 |
| ✅**DoS / TTL**              | `asyncio.wait_for` + `contextmanager` 自動清理，超時不殘留                   | 已強化 |
| ✅**Elevation of Privilege** | 結合 Phase 162 Guardrails，攔截 `sudo`, `rm -rf`, `chmod 777` 等黑名單指令 | 已整合 |
| ✅**資源隔離**               | `ContextScopeRouter` 動態載入，未授權路徑直接 403                              | 已強化 |
| ✅**防呆 Fallback**          | 循環依賴/鎖衝突/TTL 觸發 → 自動降級 Sequential + 標記 `[EXEC_FALLBACK]`       | 已納入 |

---

### 🔹 五、 下一步行動建議 (GSD 優先序)

1. **🔨 實作 `dag.py` 與拓撲排序單元測試**：模擬含循環依賴與平行分支的 `ConsensusResult`，驗證 `TopologicalSorter` 與降級邏輯。
2. **🔒 串接 `lock_manager.py` 與 `git add` 流程**：確保邏輯鎖釋放與 Git 暫存狀態一致，測試併發寫入同檔的序列化行為。
3. **📦 整合 `Validation Gate`**：寫入 `.validation/hooks.yaml`，定義 lint/test 命令與失敗回傳格式，對接 Phase 168 Reflection Loop。
4. **🌐 CLI `Live` Tree 開發**：使用 `rich` 渲染 DAG 狀態 (`[⏳] Waiting`, `[🔒] Locked`, `[🚀] Executing`, `[✅] Staged`)，提供即時 Diff 預覽與 TTL 倒數。
5. **📊 審計與資源監控對接**：將 `execution_audit.log` 格式對齊 Phase 143/165 Token Monitor，確保執行階段消耗可追蹤、可預警。

是否需要我提供：

- `ContextScopeRouter` 的動態路徑過濾邏輯與 Prompt 注入模板？
- `Validation Gate` 的 Hook 執行器與錯誤解析器 (`stderr` → `ReflectionPayload`)？
- `rich` CLI 拓撲進度樹與即時 Diff 渲染完整程式碼？

可直接指定切入點，我將輸出可立即整合至 `scripts/execution/` 的生產級模組。

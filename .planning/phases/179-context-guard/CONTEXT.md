# Phase 179 — Universal Context Guard & Safe Executor
## CONTEXT.md — Discuss Stage (v2.0 全域版)
> Generated: 2026-05-17 | Author: Tom (Senior Architect)
> 範圍：Platform 級，不限 Invoice SOP

---

## 🎯 問題重新定義 (Universal Scope)

Invoice SOP 只是**冰山一角**。任何長時間 Agent 任務都有相同風險：

| 場景 | Token 爆炸風險 | Shell 混淆風險 |
|------|--------------|--------------|
| Invoice SOP (50+ 圖片) | ✅ 已發生 | ✅ 已發生 |
| FPGA Vivado Log 分析 | 高（log 超大） | 高（Make/Tcl 混用）|
| 多目錄批次處理任務 | 高 | 中 |
| 任何跨對話長任務 | 高 | 低 |

**DoD 條件（平台層）：**
- [ ] 任何 SOP/Workflow 執行時，Token 使用量可被追蹤與強制控制
- [ ] 當接近上下文限制時，系統**自動**產生 handoff 並提示使用者
- [ ] 所有 Shell 指令（run_command）在平台層被攔截，危險操作轉換為 Python safe ops
- [ ] 上述保護對所有現有 SOP 透明（無需逐個修改）

---

## 🔍 架構現狀審計（關鍵發現）

### 已存在但斷路的基礎設施

```
src/core/
├── auto_compressor.py      ← L1/L2/L3 壓縮管線 ✅ 存在
├── workflow_checkpoint.py  ← HMAC 簽名斷點儲存 ✅ 存在
├── session_manager.py      ← AutoCompressor 整合 ⚠️ 閾值從未更新
├── harness_gateway.py      ← # Future: context_guard ⚠️ TODO 未實作
└── feature_flags.py        ← AA_ASYNC_COMPRESSION ⚠️ 預設關閉
```

**問題根因**（用電路比喻）：
```
AutoCompressor ──╌╌╌╌✗ token_count 永遠是 0（從未被記入）
CheckpointManager ──╌╌✗ SOP 層從未呼叫 save()
HarnessGateway ──╌╌╌╌✗ Security 服務是 no-op（TODO 留白）
```

**所以方案核心 = 接線（Wire Up），不是重建（Rebuild）**

---

## 🏗️ 最終架構決策

### 採用方案：C — Core Layer `ContextGuard` + 接線現有系統

```
                    ┌─────────────────────────────────────────┐
                    │      HarnessGateway._init_security()    │
                    │  (harness_gateway.py:288 — 現有 TODO 點) │
                    └──────────┬──────────────────────────────┘
                               │ 注入 ContextGuard
                               ▼
         ┌─────────────────────────────────────────────────────┐
         │          src/core/context_guard.py  [NEW]           │
         │                                                      │
         │  ┌─────────────────┐  ┌──────────────────────────┐  │
         │  │  TokenBudget    │  │   SafeShellInterceptor   │  │
         │  │  Tracker        │  │                          │  │
         │  │                 │  │ run_cmd() → safe 等效    │  │
         │  │ estimate()      │  │ rm → shutil.rmtree()     │  │
         │  │ check_budget()  │  │ mv → shutil.move()       │  │
         │  │ should_pause()  │  │ mkdir → Path.mkdir()     │  │
         │  └───────┬─────────┘  └───────────┬──────────────┘  │
         │          │                        │                  │
         │          └────────────┬───────────┘                  │
         │                       │                              │
         │          ┌────────────▼──────────────┐               │
         │          │   HandoffEmitter           │               │
         │          │                           │               │
         │          │ emit_warning()            │               │
         │          │ save_handoff()            │               │
         │          │ load_handoff()            │               │
         │          └────────────┬──────────────┘               │
         └───────────────────────│─────────────────────────────┘
                                 │ 接線現有系統
                      ┌──────────┴────────────┐
                      │                        │
                      ▼                        ▼
            CheckpointManager          AutoCompressor
            (workflow_checkpoint.py)   (auto_compressor.py)
                 [已存在]                   [已存在，修復閾值]
```

### 方案比較（為什麼選 C）

| 維度 | A: Script 層修補 | B: Workflow 文件規範 | C: Core 層注入 ✅ |
|------|---------------|-----------------|-----------------|
| 覆蓋範圍 | 只有 Invoice | 靠 AI 自律 | **所有 SOP 自動保護** |
| 後期維護 | 每個 SOP 都改 | 文件老化失效 | **一處改，處處生效** |
| 可測試性 | 困難 | 無法自動測試 | **pytest 單元測試** |
| 侵入性 | 修 SOP engine | 無侵入 | **低侵入，接線不重建** |
| 對現有 SOP 透明 | ❌ | ✅ | **✅ + 強制執行** |

---

## 📋 Phase 179 實作計畫（4 Tasks）

### Task 1: `src/core/context_guard.py` — 核心模組 [NEW]

**職責**：
1. `TokenBudgetTracker` — 估算 Token，追蹤單對話 Token 累計
2. `SafeShellInterceptor` — 轉換危險 Shell 指令為 Python safe ops  
3. `HandoffEmitter` — 產生標準化 handoff.json + 使用者警告

**關鍵 API**：
```python
class ContextGuard:
    def __init__(self, context_limit: int = 200_000, warn_threshold: float = 0.70)
    
    # Token 預算
    def track_tool_call(self, tool_name: str, content: str) -> None
    def get_usage_ratio(self) -> float          # 0.0 - 1.0
    def should_pause(self) -> bool              # > warn_threshold
    
    # Safe Shell
    def safe_run(self, cmd: str) -> SafeRunResult  # 分析並轉換
    def safe_move(self, src, dst) -> bool
    def safe_delete(self, target, whitelist: list) -> bool
    def safe_mkdir(self, path) -> bool
    
    # Handoff
    def save_handoff(self, task_state: dict) -> Path
    def load_handoff(self, path) -> Optional[dict]
    def emit_pause_warning(self) -> str         # 給 LLM 的提示文字
```

**SafeShellInterceptor 分析矩陣**：

```python
SAFE_MAPPINGS = {
    # 危險指令     → Python safe 等效
    r"rm -rf":   "shutil.rmtree() with whitelist check",
    r"del /Q":   "pathlib.Path.unlink() per file",
    r"Remove-Item.*\*": "BLOCKED — too broad, require explicit list",
    r"move":     "shutil.move() with rollback on failure",
    r"mkdir":    "Path.mkdir(parents=True, exist_ok=True)",
}
```

### Task 2: 接線 `harness_gateway.py` — 啟用 ContextGuard

**修改位置**: `_init_security()` (line 286-289)

```python
# 現在 (no-op)
def _init_security(self):
    self.logger.debug("Security Sentinel: no-op")

# 修改後
def _init_security(self):
    from .context_guard import ContextGuard
    context_limit = self.config.get("context_guard", {}).get("limit", 200_000)
    warn_ratio = self.config.get("context_guard", {}).get("warn_ratio", 0.70)
    self.context_guard = ContextGuard(context_limit, warn_ratio)
    self.logger.info(f"ContextGuard active: limit={context_limit:,}, warn={warn_ratio:.0%}")
```

### Task 3: 修復 `session_manager.py` — 啟用壓縮閾值

**問題**: `token_count` 有欄位但從未累加

```python
# 在 session.add_message() 之後加入：
session.token_count += len(content) // 4  # 啟發式估算

# 修復閾值（1000 太低，改為正確比例）：
if session.token_count > context_guard.context_limit * 0.70:
    self._compressor.compress_async(...)
```

### Task 4: Handoff Schema 標準化 (通用格式)

```json
{
  "schema_version": "2.0",
  "guard_version": "179",
  "task_type": "invoice_sop | fpga_analysis | generic",
  "session_id": "uuid",
  "context_snapshot": {
    "tokens_used": 142000,
    "context_limit": 200000,
    "usage_ratio": 0.71
  },
  "task_state": {
    "last_completed_step": "wave_2",
    "processed_items": [...],
    "failed_items": [],
    "next_action": "continue_wave_3"
  },
  "artifacts": {
    "output_dir": "temp/atomic_json",
    "state_file": "temp/state_temp.json",
    "index_file": "temp/file_index.json"
  },
  "resume_instructions": "新對話開始時，讀取此 handoff 並從 next_action 繼續",
  "timestamp": "2026-05-17T12:00:00+08:00",
  "hmac": "<sha256 integrity>"
}
```

---

## 🔐 STRIDE 資安分析

| 威脅 | 具體場景 | 防禦 |
|------|---------|------|
| **S (Spoofing)** | 偽造 handoff.json 跳過已完成步驟 | HMAC 簽名驗證（沿用 CheckpointManager）|
| **T (Tampering)** | 修改 context_limit 允許 Token 爆炸 | config 讀取後鎖定，不可動態修改 |
| **R (Repudiation)** | 無法確認哪個 Shell 指令觸發刪除 | SafeShellInterceptor 記錄所有操作到 audit log |
| **I (Info Disclosure)** | handoff 包含敏感發票數據 | `.agent-state/` 排除 git，handoff 不含原始內容只含 hash |
| **D (Denial of Service)** | safe_delete 被誤用 | 白名單：只允許刪除 `temp/`、`.agent-state/` 下的已知路徑 |
| **E (Elevation)** | Shell 指令包含特權操作 | 禁止清單：`sudo`、`format`、`drop table`、`rm /` |

---

## ⚙️ 效能設計

- Token 估算：啟發式 `len(content) // 4`，O(1)，無額外依賴
- HandoffEmitter：背景線程寫入，不阻塞主流程
- 攔截開銷：正則匹配 < 1ms，可忽略

---

## 🧪 測試策略

| 層次 | 測試項目 | 工具 |
|------|---------|------|
| 單元 | TokenBudgetTracker 計算正確性 | pytest |
| 單元 | SafeShellInterceptor 危險指令識別 | pytest + 參數化 |
| 單元 | HandoffEmitter HMAC 完整性 | pytest |
| 整合 | SessionManager token_count 累加 | pytest + mock LLM |
| 整合 | HarnessGateway 啟動 ContextGuard | pytest + tmp_path |
| 迴歸 | safe_delete 拒絕白名單外路徑 | pytest |
| 手動 | 實際 Invoice SOP 處理 `z:\01` | 人工驗證 handoff 輸出 |

---

## 📁 交付物清單

```
src/core/context_guard.py              [NEW] ← 核心模組（~200 行）
src/core/harness_gateway.py            [MODIFY] ← 2 行接線
src/core/session_manager.py            [MODIFY] ← 修復 token_count 累加 + 閾值
tests/test_context_guard.py            [NEW] ← 完整單元測試
docs/context_guard.md                  [NEW] ← 使用說明
config/harness.toml                    [MODIFY] ← 加入 [context_guard] section
```

---

## 📡 對現有 SOP 的影響（透明保護）

| SOP 類型 | 需要修改？ | 自動受保護？ |
|---------|---------|-----------|
| Invoice SOP | ❌ | ✅ 自動 |
| FPGA 分析 SOP | ❌ | ✅ 自動 |
| 未來任何新 SOP | ❌ | ✅ 自動 |
| OpenClaw 工作流 | ❌ | ✅ 自動（透過 Gateway） |

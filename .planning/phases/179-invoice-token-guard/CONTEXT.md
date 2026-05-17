# Phase 179 — Invoice Token Guard & Safe Shell Protocol
## CONTEXT.md (Discuss Stage)
> Generated: 2026-05-17 | Author: Tom (Senior Architect)

---

## 🎯 Phase 目標 (DoD)

解決 Invoice SOP 在處理大型目錄（50+ 檔案）時的兩個根本性問題：
1. **Context Bloat → Token 耗盡**：連續 `view_file` 導致 LLM 上下文爆炸，Agent 開始行為異常
2. **Shell 環境混淆 → 自毀事故**：PowerShell 的 `del`/`rm`/`&&` 混用，導致已完成的 atomic JSON 被意外刪除

**DoD 條件：**
- [ ] SOP Engine 能自動追蹤 Token 預算，並在閾值前主動暫停並輸出 handoff
- [ ] 所有檔案操作改用 Python `shutil`/`os`，完全移除 Shell 指令依賴
- [ ] handoff.json 格式標準化，支援跨對話斷點續傳
- [ ] 新對話載入 handoff 後能精確從上次 Wave 繼續

---

## 📍 根本原因 (RCA)

### Bug 1: Context Window Exhaustion

| 行為 | 影響 |
|------|------|
| 每張發票圖片（JPG/PDF）呼叫 `view_file` 進行視覺提取 | 每次 ~2000-5000 tokens（含圖像 base64）|
| 50 個檔案 × 平均 3000 tokens | 上下文累計 ~150K tokens |
| Wave 間不清理歷史 | 舊對話數據持續佔用 context 窗口 |
| 處理完 `z:\02` 再接 `z:\01` | Context 已飽和，Token 耗盡觸發異常 |

**關鍵觀察**：`workflow_checkpoint.py`（Phase 134 產出）是通用架構層工具，**沒有針對 Invoice SOP 的自動觸發邏輯**。Phase 134 已 DONE，但 SOP Engine 層從未整合這個 checkpoint。

### Bug 2: Shell Command Logic Error (PowerShell)

```
# 事故重現（來自 test_01_bug.md）
del /Q temp\atomic_json\*             # 失敗！PowerShell 不支援 /Q
move temp\atomic_wave_*.json temp\atomic_json\  # 但 move 成功了！

# 下一步（災難）
Remove-Item -Path temp\atomic_json\* -Force  # atomic_wave 已在裡面，全刪！
```

**根因**：Token 耗盡後 Agent 思維混亂 → 用混合 Shell 語法 → `&&` 無效但副作用殘留 → 第二條指令清掃全部。

---

## 🏗️ 架構決策

### 方案比較

| 維度 | 方案 A (修改 SOP Engine) | 方案 B (獨立 HandoffManager) |
|------|-------------------------|------------------------------|
| 職責分離 | ❌ SOP engine 職責過重 | ✅ 單一職責，可獨立測試 |
| 侵入性 | ⚠️ 修改 sop_v7_engine.py | ✅ 新建，不碰現有 |
| 復用性 | ❌ 綁定 Invoice SOP | ✅ 可供其他 SOP 使用 |
| 架構合規 | ❌ scripts/ 呼叫 core/ | ✅ 遵循分層原則 |

**決策：採用方案 B** — 新建 `scripts/invoice_handoff_manager.py`，SOP Engine 透過 bridge 呼叫。

### 系統架構圖

```
                    ┌─────────────────────────────────┐
                    │       sop_v7_engine.py           │
                    │  (Wave 1 → Wave 2 → Wave N)     │
                    └──────────┬──────────────────────┘
                               │ 每 Wave 結束
                               ▼
                    ┌─────────────────────────────────┐
                    │   InvoiceHandoffManager          │
                    │   scripts/invoice_handoff_mgr.py │
                    │                                  │
                    │  ① estimate_token_usage()        │
                    │  ② check_budget_threshold()      │  ← 觸發條件: > 70% context
                    │  ③ save_handoff()                │  ← 寫入 handoff.json
                    │  ④ emit_warning()                │  ← 提示使用者開新對話
                    │  ⑤ safe_file_ops()              │  ← 替代 Shell 指令
                    └──────────┬──────────────────────┘
                               │
                               ▼
                    ┌─────────────────────────────────┐
                    │   handoff.json (State File)      │
                    │   .agent-state/invoice_handoff/  │
                    └─────────────────────────────────┘
```

---

## 📋 實作計畫 (3個任務)

### Task A: InvoiceHandoffManager 核心
**檔案**: `scripts/invoice_handoff_manager.py`

```python
# 核心功能
class InvoiceHandoffManager:
    MAX_CONTEXT_RATIO = 0.70    # 70% 閾值觸發警告
    MAX_IMAGES_PER_WAVE = 8     # 每 Wave 最多處理 8 個圖片
    
    def save_handoff(self, wave_id, processed_files, summary) -> Path
    def load_handoff(self, handoff_path) -> dict
    def check_should_pause(self, files_processed_count) -> bool
    def safe_move(self, src, dst) -> bool   # 替代 mv/move
    def safe_delete(self, target) -> bool   # 替代 rm/del（帶確認）
    def safe_mkdir(self, path) -> bool      # 替代 mkdir
```

### Task B: handoff.json Schema 標準化
**位置**: `.agent-state/invoice_handoff/<timestamp>_handoff.json`

```json
{
  "schema_version": "1.0",
  "project_root": "z:\\01",
  "session_id": "uuid",
  "last_completed_wave": 2,
  "processed_files": ["01/114012月勞保-1.jpg", ...],
  "failed_files": [],
  "summary": {
    "total": 50, "done": 20, "failed": 0,
    "total_amount": 189234,
    "categories": {"保險費": 3, "旅費": 23}
  },
  "next_action": "continue_wave_3",
  "next_files": ["01/進口報單/0130-4.jpg", ...],
  "atomic_json_dir": "temp/atomic_json",
  "state_temp_path": "temp/state_temp.json",
  "timestamp": "2026-05-17T12:00:00+08:00",
  "resume_prompt": "請載入 handoff 繼續 Wave 3，已忽略歷史詳細日誌"
}
```

### Task C: SOP Engine 整合 Hook
**修改**: `scripts/sop_v7_engine.py`（低侵入性）
- 在每個 Wave 結束後呼叫 `handoff_mgr.save_handoff()`
- 在開始前呼叫 `handoff_mgr.load_handoff()` 檢查是否有未完成任務
- 替換所有 Shell 指令為 `handoff_mgr.safe_*()` 方法

---

## 🔐 資安 STRIDE 分析

| 威脅 | 描述 | 防禦措施 |
|------|------|---------|
| **T (Tampering)** | handoff.json 被篡改 → 跳過已完成項目 | 沿用 `CheckpointManager` 的 HMAC 簽名 |
| **R (Repudiation)** | 無法確認哪個 Wave 被刪除 | handoff 記錄每個 Wave 的 SHA-256 hash |
| **I (Info Disclosure)** | handoff 包含發票金額等敏感數據 | `handoff.json` 加入 `.gitignore`，僅存放 `.agent-state/` |
| **D (Denial of Service)** | safe_delete 被誤用刪除整個目錄 | 強制要求目標必須是「已知安全路徑」白名單 |

---

## ⚙️ 非功能性需求

- **效能**：Token 估算使用輕量啟發式（字元數 / 4），不引入額外依賴
- **跨平台**：所有 Path 操作使用 `pathlib`，確保 Windows/Linux 均正常
- **可恢復性**：handoff 即使在 Wave 中斷時也能儲存當前部分進度

---

## 🧪 測試策略

| 測試層 | 內容 | 工具 |
|--------|------|------|
| 單元測試 | `save_handoff` / `load_handoff` / `safe_move` | pytest |
| 整合測試 | 模擬 50 個檔案處理，觸發 70% 閾值 | pytest + 假 `file_index.json` |
| 迴歸測試 | 確認 `safe_delete` 不會刪除非白名單目錄 | pytest + tmp_path |
| 手動 UAT | 實際處理 `z:\01`，驗證 handoff 自動輸出 | 人工驗證 |

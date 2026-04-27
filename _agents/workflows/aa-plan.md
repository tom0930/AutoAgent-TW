---
description: Plan & Research Phase N / 研究 + 規劃階段 N。
---

# AutoAgent-TW Plan Workflow

## Input
- Phase number: N (from $ARGUMENTS)

// turbo-all

## Steps

### Step 0: Context Guard 前置檢查 (Active Context Defense)
1. 檢查 `.geminiignore` 是否存在。若不存在，自動執行：
```bash
python scripts/context_guard.py .
```
2. 掃描工作區中 >500KB 的非原始碼檔案，預估 Token 佔用。
3. 若預估 Token > 100K → 發出 ⚠️ 警告並建議瘦身。
4. 確認安全後才進入 Step 1。

### Step 1: 匯入上下文
1. 讀取 `.planning/PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`。
2. 讀取 `.planning/phases/{N}-*/CONTEXT.md` 以確定當前階段的設計決策。

### Step 2: 階段性領域研究 (Session Research)
針對 Phase N 的具體組件：
1. 獲取現有文件的代碼地圖 (Codebase Map)。
2. 分析與 Phase N 相關的 API 與資料結構。
3. 如果需要，使用 `search_web` 搜尋技術實現方案。
4. 產出 `RESEARCH.md` 內容：實施方案分析、依賴檢查、已識別的陷阱。

### Step 3: 定義執行計畫 (Atomic Splitting)
1. **複雜度評估**：計算本 Phase 任務的總步數與檔案跨度。
2. **決策拆單**：
- **若內容單純**：產出單一 `.planning/phases/{N}-*/PLAN.md`。
- **若內容複雜 (涉及多模組、外部認證、步數 > 10)**：將 Phase ${N} 強制拆分為子任務檔案：
    - `task_1_setup.md`
    - `task_2_implementation.md`
    - `task_3_verification.md`
3. 每個任務需包含：目標、具體步驟、預期變更的文件列表，以及對應的驗證標準 (UAT Criteria)。

### Step 3.5: 8 維度檢查表（強制 Markdown 表格）
> 從 user_rules 下放至此的執行細節。每個 Plan 必須通過：

| # | 維度 | 檢查項 |
|---|------|--------|
| 1 | 需求拆解 | 邊界定義完整？ |
| 2 | 技術選型 | 有理由？有替代方案？ |
| 3 | 架構圖 | Mermaid 文字圖完整？ |
| 4 | 並行設計 | 鎖策略、死鎖預防？ |
| 5 | 資安威脅 | STRIDE + Prompt Injection 防禦？ |
| 6 | AI 考量 | UX、成本、模型漂移？ |
| 7 | 錯誤處理 | 監控與恢復策略？ |
| 8 | 測試策略 | 單元/整合/E2E/壓力/資安？ |

### Step 3.6: 驗證合約生成 (Verification Contract)
> **Karpathy**: 「Don't tell it what to do, give it success criteria and watch it go.」

1. 從 `_agents/templates/verification_contract.yaml` 複製模板至 `.planning/phases/{N}-*/`。
2. 為每個任務填入**具體的、機器可執行的**成功標準。
3. ❌ 禁止模糊 UAT：「功能正常」「測試通過」。
4. ✅ 正確 UAT：`python -m pytest tests/test_xxx.py -v` → `exit_code == 0`。
5. 設定 `max_fix_loops: 3` 與 `negative_patterns`。

### Step 4: 狀態更新與 Commit
1. 更新 `.planning/STATE.md`。
2. Commit 研究與計畫：
```bash
git add .planning/phases/
git commit -m "docs: phase ${N} domain research and implementation plan"
```

### Step 5: 建議下一步
1. 提示執行 `/aa-execute N` 開始進入執行階段。
2. 交互模式下邀請使用者審閱計畫。

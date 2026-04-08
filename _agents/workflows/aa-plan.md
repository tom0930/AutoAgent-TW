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

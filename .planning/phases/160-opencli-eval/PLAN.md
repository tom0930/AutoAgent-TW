# Implementation Plan - Phase 160: AutoCLI Integration

## 1. 任務目標 (Objectives)
將 `nashsu/AutoCLI` (Rust) 整合為 AutoAgent-TW 的 `Eye-2` (Web/CDP) 引擎，實現低資源消耗的結構化網頁抓取。

## 2. 任務拆解 (Atomic Tasks)

### Wave 1: 環境佈署 (Infrastructure)
- **Task 1.1**: 確認 `bin/` 目錄存在，並檢索 AutoCLI 官方下載連結。
- **Task 1.2**: 使用 PowerShell 指令下載並解壓縮 `autocli.exe` 至 `bin/`。
- **Task 1.3**: 驗證 `autocli --version` 確保執行檔正常。

### Wave 2: Skill 介面開發 (Skill Implementation)
- **Task 2.1**: 創建 `openclaw/skills/autocli/` 目錄。
- **Task 2.2**: 撰寫 `SKILL.md`，封裝 `fetch` 與 `list-adapters` 功能。
- **Task 2.3**: 整合至 `mcp-router` 的工具發送鏈。

### Wave 3: 資安強化 (Security Hardening)
- **Task 3.1**: 更新 `scripts/context_guard.py` 或 `mcp-router`，加入網域黑/白名單檢查。
- **Task 3.2**: 實作 `Stealth Mode` 監控，確保抓取時記憶體不超過 50MB 閾值。

### Wave 4: 驗證與 POC (Verification)
- **Task 4.1**: 執行 `tests/autocli.md` 中的所有測試用例。
- **Task 4.2**: 產出 `QA-REPORT.md`，記錄效能指標與通過狀況。

## 3. 預期變更檔案 (Affected Files)
- `bin/autocli.exe` (New Binary)
- `openclaw/skills/autocli/SKILL.md` (New Skill)
- `.planning/STATE.md` (Update Status)
- `tests/autocli.md` (Update Test Checkboxes)

## 4. 驗收標準 (UAT Criteria)
- [ ] `autocli fetch https://github.com` 回傳乾淨 JSON 且耗時 < 1s。
- [ ] 執行過程中，`Memory-Sentinel` 未發出超標警告。
- [ ] 試圖訪問 `google.com/finance` (假設為黑名單) 時被正確攔截。

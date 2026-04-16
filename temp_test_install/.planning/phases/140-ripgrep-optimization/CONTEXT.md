# Architectural Context: Phase 140 - Ripgrep System Optimization (v2.6.0)

## 🎯 任務目標 (Objective)
改善當前開發環境在 Windows Terminal 下的全局檢索速度。雖然 Agent 工具內建了 `grep_search`，但開發者與 Agent 在執行 `run_command` 時，原生 `grep` (若存在) 效能不佳且不支援 `.gitignore`。本階段將部署 `ripgrep (rg)` 作為核心檢索引擎。

## 🛠️ 技術選型 (Technological Decisions)
1. **工具**: `ripgrep` (Rust-based) - 目前業界最快的全局搜尋工具。
2. **部署方式**: 
   - 優先嘗試 `scoop install ripgrep` (若已安裝 Scoop)。
   - 備選方案：手動下載二進制檔並加入 `$PATH` 或專案 `_bin/` 目錄。
3. **整合**: 為 `grep` 建立 Alias 或取代建議，並更新 `scripts/` 工具鏈以利用 `rg` 進行本地預過濾。

## 🛡️ 資安威脅建模 (STRIDE)
- **S (Spoofing)**: 無。
- **T (Tampering)**: 下載 binary 時需驗證 Hashes 防止惡意替換。
- **R (Repudiation)**: 無。
- **I (Information Disclosure)**: `rg` 會遞迴掃描目錄。
  - *防禦*: 默認啟用 `--smart-case` 並確保讀取 `.gitignore`，防止意外輸出隱藏的敏感文件 (如 `.env`, `.git/`)。
- **D (DoS)**: 掃描極大規模 Repo (如 node_modules)。
  - *防禦*: 默認過濾 binary 與 ignored files，利用 `rg` 的高度並發與 ignore 機制優化效能。
- **E (Elevation of Privilege)**: 無。

## 📋 邊界定義 (DoD)
- [ ] 成功在 Terminal 執行 `rg --version`。
- [ ] 執行時間測試：在專案根目錄搜尋關鍵字需在 <50ms 內響應。
- [ ] 支援 `.gitignore` 過濾。
- [ ] 文件更新：在 `README.md` 加入 `rg` 使用說明。

## 🏗️ 編排策略 (Orchestration)
- **Mode**: Single Wave (Sequence).
- **Automation**: `--auto` (將自動嘗試路徑配置)。

---
*Signed by Tom, Senior Architect on 2026-04-15*

# GSD PLAN: Phase 140 - Ripgrep System Optimization (v2.6.0)

## 1. 任務分工 (Plan Details)

| 步驟 | 說明 | 負責組件 |
| :--- | :--- | :--- |
| **1. 自動化安裝** | 使用 `winget` 部署 `ripgrep` 核心二進制檔。 | `run_command` |
| **2. 環境校驗** | 確保 `rg` 命能在 Terminal 中被正確調用，驗證版本。 | `rg --version` |
| **3. 性能驗證** | 執行大型搜尋測試，確認其速度與 `.gitignore` 遵從性。 | Benchmark Test |
| **4. 文檔結案** | 更新 `README.md` 並產出 `QA-REPORT.md`。 | Documentation |

## 2. 具體待辦清單 (Checklist)

### Wave 1: 安裝與校驗 (Deployment)
- [ ] 執行 `winget install --id BurntSushi.ripgrep.MSVC --accept-package-agreements`。
- [ ] 執行 `refreshenv` (或手動檢查 Path) 確保 `rg` 命令可用。
- [ ] 驗證版本資訊 `rg --version`。

### Wave 2: 基礎設施優化 (Optimization)
- [ ] 在 `scripts/` 中新增一個 `fast_search.py` 範例，展示如何調用 `rg` 進行本地預過濾。
- [ ] 測試搜尋大型目錄 (如 `.planning/history/`) 是否能即時返回。

### Wave 3: 交付 (Ship)
- [ ] 更新彙報文件。
- [ ] Git Commit: `feat: 部署 ripgrep 優化全局檢索效能 v2.6.0`。

## 3. 測試腳本 (Verification Snippet)
```bash
# 驗證過濾 node_modules 等忽略目錄
rg "biggoALL" --stats
```

---
*Planned by Agent on 2026-04-15*

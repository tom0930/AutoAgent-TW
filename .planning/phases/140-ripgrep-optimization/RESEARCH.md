# Research Report: Phase 140 - Ripgrep Installation Strategies on Windows

## 1. 安裝途徑分析 (Installation Methods)

| 方案 | 工具 | 優點 | 缺點 | 結論 |
| :--- | :--- | :--- | :--- | :--- |
| **A (推薦)** | `winget` | Windows 內建，無需第三方套件管理員。 | 需要網際網路連接。 | **選用** |
| **B** | `Scoop` / `Choco` | 業界標準，版本管理強。 | 若沒裝管理員則需額外安裝流程。 | **備選** |
| **C** | `Direct Binary` | 100% 可控，無需安裝權限。 | 手動維護路徑，升級困難。 | **應急選用** |

## 2. 具體實施細節 (Implementation Details)
- **套件 ID**: `BurntSushi.ripgrep.MSVC`
- **靜默安裝參數**: `--accept-source-agreements --accept-package-agreements`
- **路徑影響**: `winget` 會自動將安裝目錄加入 `PATH`，但在當前終端視窗可能不生效，需刷新環境變數。

## 3. 效能對比 (Performance Benchmark)
根據社群數據，`rg` 在處理大型專案時比 `grep` 快 10-50 倍，且具備：
- 默認遞迴
- `.gitignore` 識別
- 多核並行掃描 (SIMD 優化)

## 4. 安全性驗證 (Security Context)
- `winget` 提供雜湊值校驗。
- 安裝後無需管理員權限即可在 User 權限下運行 (User scope)。

---
*Created on 2026-04-15*

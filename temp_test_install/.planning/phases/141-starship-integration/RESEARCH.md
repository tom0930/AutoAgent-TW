# Research Report: Phase 141 - Starship & Token Optimization

## 1. 安裝與整合 (Installation)
- **Winget ID**: `Starship.Starship`
- **Shell Support**: 完美支持 PowerShell, Bash, CMD, Fish。
- **配置目錄**: `%USERPROFILE%\.config\starship.toml`

## 2. Token 優化策略 (Token Optimization Strategy)

| 模組 | 預設行為 | 建議優化 | 效果 |
| :--- | :--- | :--- | :--- |
| **Directory** | 顯示全路徑 | `truncate_to_repo = true`, `truncation_length = 2` | 減少 50% 以上的路徑字元。 |
| **Cmd Duration** | 顯示執行時間 | `disabled = true` (Agent 模式) | 避免日誌中出現 `2s` 等變動數據，降低不穩定噪音。 |
| **Git Status** | 顯示詳細變更數 | `disabled = true` (Agent 模式) 或極簡符號 | 防治大規模 Repo 下的 Prompt 延遲與冗餘輸出。 |
| **Battery/Hostname** | 顯示環境資訊 | `disabled = true` | 徹底排除 non-coding 相關字元。 |

## 3. 字體與視覺兼容性 (Visual Compatibility)
- **Nerd Fonts**: Starship 高度依賴編碼字符。
- **備案**: 若 User 沒裝 Nerd Font，將建立一個「Plain Text Fallback」配置，確保畫面不會出現亂碼。

---
*Created by Agent on 2026-04-15*

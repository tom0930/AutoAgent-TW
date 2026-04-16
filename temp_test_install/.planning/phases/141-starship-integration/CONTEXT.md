# Architectural Context: Phase 141 - Starship integration & Prompt Optimization (v2.7.0)

## 🎯 任務目標與意圖挖掘 (Context & Intent)
目前的開發環境在 Terminal 下缺乏直觀的狀態反饋（如當前 Git 分支、Python 虛擬環境、Rust 版本等）。
安裝 **Starship** 不僅是為了美化 User (Tom) 的終端體驗，更重要的是透過「Prompt 標準化」來優化 Agent 的 Context 管理。

### 關於 Token 的改善 (Token Optimization)
1. **減少 Prompt 冗餘**: 傳統的 Bash/PowerShell Prompt 若包含長路徑、複雜格式，在 Agent 的歷史對話紀錄 (Logs) 中會佔用大量 Token。
2. **單行化與精簡**: 透過 Starship 配置一個「Agent 專用精簡模式 (Mini-Prompt)」，在執行 `run_command` 時，確保對話紀錄中不包含重複的系統資訊。
3. **Context 維護**: 讓 Agent 能從提示字元中立即辨識當前是否在正確的 Branch 或 venv，減少執行 `git branch` 或 `python --version` 的次數。

## 🛠️ 技術選型與 Trade-off (Architecture & Decisions)
- **工具**: **Starship** (Rust 撰寫，跨 Shell 支持)。
- **優點**: 極速 (Rust SIMD 優化)、高度可定製 (TOML)、支持所有主流 Shell (Cmd, PowerShell, Bash)。
- **決策**: 
  - 使用 `winget` 或 `scoop` 進行安裝。
  - 產出一份專屬的 `starship.toml` 配置文件，平衡「視覺美觀」與「Agent 理解」。

## 🛡️ 資安威脅建模 (STRIDE)
- **S (Spoofing)**: 無。
- **T (Tampering)**: 確保從官方渠道下載。
- **R (Repudiation)**: 無。
- **I (Information Disclosure)**: 避免在 Prompt 中顯示自定義的敏感環境變數。
- **D (DoS)**: 無 (Starship 是目前效能最好的 Prompt 引擎)。
- **E (Elevation of Privilege)**: 無。

## 📋 邊界定義與驗收標準 (DoD)
- [ ] 成功安裝 Starship 並配置於 PowerShell/Cmd。
- [ ] 能夠正確顯示 Git 分支、Python 虛擬環境標誌。
- [ ] 提供 `Agent-Optimized` 配置，減少冗餘字符以節省 Token。
- [ ] 更新 `README.md` 開發工具章節。

## 🏗️ 編排策略 (Orchestration)
- **Mode**: Single Wave.
- **Automation**: `--auto` (自動偵測當前 Shell 配置文件進行注入)。

---
*Signed by Tom, Senior Architect on 2026-04-15*

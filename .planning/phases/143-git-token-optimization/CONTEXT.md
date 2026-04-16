# CONTEXT.md (Phase 143: Git Token Optimization - GTK)

## 📌 意圖與目標 (Intent & Goals)
本階段目標為解決 GitKraken MCP 在大型專案 (FPGA, MFC C++) 查詢 diff 時造成的 Token 浪費問題。將透過整合 RTK (Rust Token Killer) 技術，將日常版本控制查詢的 Token 消耗壓縮 **75-93%**，確保 AutoAgent-TW 能以低成本高頻率監控本地狀態。

## 🎯 DoD (Definition of Done)
1. 成功建立 `git-token-killer` 技能，並整合 `rtk git` wrapping。
2. 配置 `rtk-git-config.toml` 以涵蓋針對不同語言/環境的壓縮邏輯。
3. `gitmcp.md` (Git Operational Protocol) 更新完成，引導 AI 預設使用優化配置。
4. Status Notifier 增加 Git Token 節省率的追蹤機制。

## 🏛️ 架構選型 (Architecture Selection)
**Option A（已選用）**: **Hybrid Optimized Skill (git-token-killer)**
- **設計**：藉由 Python Wrapper 攔截 `git` 指令，將 stdout 導流給 `rtk` 壓縮。並透過環境變數 `AUTOAGENT_PHASE` 動態選擇 `--compact`, `--summary`, `--verbose`。
- **Trade-off**：需要建立新技能目錄與腳本，但能提供最高程度的自動化與過濾精細度，且能保留 GitKraken MCP 以備深度查詢之需。

## 🛡️ 資安與威脅建模 (STRIDE)
1. **Spoofing**：無，純本地腳本過濾。
2. **Tampering**：Wrapper 取代原生輸出。防禦：提供 `--raw` fallback。
3. **Information Disclosure（高風險）**：過度壓縮可能隱藏敏感資訊洩漏的安全警告。
   - **防禦**：`Guardian Phase` 強制啟動 `--verbose` 模式，並設定遇到 `error` 時觸發 `fallback_on_error = true` 保留完整輸出。
4. **Denial of Service**：RTK 解析極大 diff 可能佔用 CPU。
   - **防禦**：使用 Rust 開發的 rtk 本身具備高效特性，且預設 `--stat` 模式僅抓取 metadata。

## 🔄 編排與並行 (Orchestration)
- 本任務相對獨立且為基礎設施增益，不適合 Wave 並行化。
- 後續將在 Dashboard 透過 Side-Channel 機制呈現 `rtk gain` 的精簡幅度，避免佔用主要對話 Context。

---
*Created per GSD v2.1 Workflow.*

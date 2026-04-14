# AutoAgent-TW 進階整合專案 (v1.9.0 - v2.4.0)

## 專案背景與目標
為了彌平 AutoAgent-TW 與高級 AI 編碼代理 (如 Claude Code) 之間的差距，本計畫基於 `cc_adv.md` 方案，將現有 AutoAgent-TW 架構升級為具備六大核心能力的新一代架構。利用全新的 `.planning1` 作為規劃區，與舊版 `.planning` 隔離，保障新架構研發的獨立性。

## 核心價值
1. **子代理系統與平行任務調度**：突破線性執行，引進 Spawn Manager 與 Coordinator 實現動態拆解與平行執行。
2. **MCP 架構整合**：提供無限擴充工具能力。
3. **工作流客製化**：透過 CLAUDE.md 及 hooks 機制，實現團隊工作流與編碼規範定製。
4. **專案記憶與上下文管理**：實作 L1/L2/L3 記憶分層與對話自動壓縮，避免遺忘架構決策。
5. **智慧預測引擎**：主動提供指令建議，將 AutoAgent 由被動等待升級為主動提供。
6. **無頭模式與持續整合**：完美銜接 CI/CD 與 GitHub Actions，具備自動 PR Review 功能。

## 技術棧
- Python 3.10+
- `anthropic>=0.39.0` (Claude API)
- `mcp>=1.0.0` (MCP 客戶端)
- `faiss-cpu>=1.8.0` (向量檢索)
- `pygithub>=2.4.0` (GitHub 整合)

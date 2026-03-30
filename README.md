# AutoAgent-TW: Advanced Autonomous Agent System

[![Version](https://img.shields.io/badge/version-1.4.0--stable-green)](https://github.com/tom0930/AutoAgent-TW)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 繁體中文介紹 (Introduction)

**AutoAgent-TW** 是一套專為 Antigravity IDE 打造的高級自主開發代理系統。
它基於 L3/L4 級別的自動化邏輯，能自動完成從「需求規劃」到「程式碼實作」再到「品質 QA」的全生命週期開發流程。

### 核心功能 (Key Features)

1.  **一鍵建構 (Auto-Build)**: 使用 `/aa-auto-build` 啟動全自動開發模式。
2.  **自我修復 (Self-Repair)**: 當代碼測試失敗時，系統會自動診斷並重寫，直到通過（最多 3 輪）。
3.  **三位一體 Agent**:
    - **Builder**: 執行開發與實作。
    - **QA**: 嚴格的品質把關。
    - **Guardian**: 安全審計與 Checkpoint 管理。
4.  **中斷恢復**: 指令中斷後可使用 `/aa-resume` 無縫恢復上次進度。

---

## 🛠 安裝步驟 (Installation)

1.  **環境要求**:
    - Antigravity IDE
    - Git / Node.js / Python 3.10+
2.  **下載與配置**:
    ```bash
    git clone https://github.com/tom0930/AutoAgent-TW.git
    cd AutoAgent-TW
    ```
3.  **註冊 Skills**:
    將 `AutoAgent-TW` 目錄下的核心邏輯註冊到 Antigravity 技能系統（詳見 `aa-installer` 腳本）。

---

## ⚖️ 免責聲明 (Disclaimer)

使用本專案前請務必閱讀以下條款：
1. **自主行為風險**: 本系統具有自主修改程式碼與執行命令之能力，使用者需對其指令產生的最終後果負責。
2. **程式碼正確性**: 雖然具備 QA 與自癒機制，但不保證產出的代碼完全無誤，建議在生產環境使用前進行二次審核。
3. **資料安全**: 請勿在專案目錄下放置未加密的敏感金鑰（API Keys/Passwords），以免被 Agent 誤傳或處理。

---

## 👨‍💻 English Summary

**AutoAgent-TW** is an autonomous agent system for Antigravity IDE. It orchestrates Builder, QA, and Guardian agents to automate full-stack development cycles.

- **Auto-Build**: One command to build projects end-to-end.
- **Self-Fix**: Automated bug diagnostic and repair loops.
- **Guardian**: Integrated security auditing and state management.

---
*Created by [tom0930](https://github.com/tom0930)*

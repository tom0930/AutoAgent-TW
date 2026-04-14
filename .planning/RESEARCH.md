# RESEARCH: AutoAgent-TW Installer Requirements

## 1. 現狀分析 (Current State)
- **核心邏輯**: 已存在 `scripts/aa_installer_logic.py`，內容非常完整，包含 Git 設定、專案初始化、venv 建立、OpenClaw 部署、PATH 註冊、MemPalace 初始化等。
- **缺失組件**: 
    - 缺乏一個對 Windows 用戶友好的入口腳本 (Bootstrapper)。
    - 現有邏輯過於依賴互動式輸入 (`input()`)，在自動化場景下較慢。
    - 缺乏全域命令 `aa-tw` 的別名（目前是 `autoagent`）。
- **依賴項**: Python 3.10+, Node.js (for OpenClaw), Git.

## 2. 目標 (Objectives)
- 建立一個 `aa-installer.ps1`。
- 優化 `aa_installer_logic.py` 支援 `--auto` 參數。
- 確保全域指令 `autoagent` 與 `aa-tw` 皆可運作。

## 3. 關鍵路徑 (Critical Path)
1. 建立 PS1 引導程式。
2. 注入資安檢查（檢查檔案完整性與 PATH 過長限制）。
3. 自動化環境變數生效通知。

## 4. 參考檔案
- [aa_installer_logic.py](file:///z:/autoagent-TW/scripts/aa_installer_logic.py)
- [requirements.txt](file:///z:/autoagent-TW/requirements.txt)

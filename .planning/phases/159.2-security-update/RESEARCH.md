# Phase 159.2 Domain Research: Security Documentation Hardening

## 1. 實施方案分析 (Implementation Analysis)
根據 `CONTEXT.md` 決策，我們將在 `z:\autoagent-TW\SECURITY.md` 檔案中加入一個全新的章節：**Runtime Resource & Extension Hardening**。

目前的 `SECURITY.md` 結構為：
1. Security Model: Local-Only
2. Potential Threats (STRIDE Analysis)
3. Protective Measures
4. Installer Security (Industrial Grade)

我們計畫將新章節插入在 **Protective Measures** 和 **Installer Security** 之間。此章節的目的是為 Phase 158.5 實作的 `pyrefly.exe.disabled` 防禦性架構提供正當性背書。

### 插入內容大綱：
**Runtime Resource & Extension Hardening (Stealth Mode)**
Antigravity 內建主動式資源隔離機制，以防護 IDE 擴展元件造成的記憶體耗盡（OOM DoS）。
1. **LSP Process Renaming**: 系統會將高資源消耗的 LSP 守護進程（如 `pyrefly.exe`）重命名為 `.disabled`，強迫其轉為按需執行的 "One-Shot CLI" 模式。
2. **Intentional Path Hijacking Mitigation**: 這是受控的系統行為，非惡意軟體劫持。任何對 `.disabled` 的啟用行為都必須透過 `shadow_check.py` 搭配內部 lock 機制 (`.pyrefly.lock`) 進行，以確保無並發競爭（Race Condition）風險。
3. **RVA Security Boundary**: 針對視覺自動化與 FPGA 工具鏈，強制實施 UIA 白名單限制，防止越權操作。

## 2. 依賴與副作用 (Dependencies & Side Effects)
- **副作用**: 僅更新純文字文件，無系統功能副作用。
- **後續依賴**: `shadow_check.py` 的並發鎖定機制（lock file）將在未來的 Phase 中進行實作，本階段先在資安模型中聲明其必要性。

## 3. 已識別的陷阱 (Identified Pitfalls)
- 直接使用 `replace_file_content` 替換可能會破壞 `SECURITY.md` 現有格式。需準確定位插入點。

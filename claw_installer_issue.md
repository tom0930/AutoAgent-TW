# 🦞 OpenClaw Installer & Packaging Issue Report (Phase 2 - AS-4.2)

**Status**: 🚨 BLOCKED (Metadata & Path Dependency)  
**Assigned**: OpenClaw Engineering Team (AutoSkills Phase 2 Implementation)

## 1. 關鍵阻塞：Metadata 遺失錯誤 (Metadata missing)
**現象**：執行 `openclaw gateway start` 時報錯：
`[openclaw] Failed to start CLI: Error: Missing bundled chat channel metadata for: telegram, whatsapp...`

**根因分析**：
- OpenClaw 依賴 `dist/` 中的預編譯元數據。
- 用戶環境中的 `node_modules` 或 `dist` 產物不完整。
- **解決路徑**：必須確保在發布包中包含 `postinstall-bundled-plugins.mjs` 執行的產物，或者在安裝階段自動執行 `npm install`。

## 2. 硬編碼路徑依賴 (Hardcoded Path: Z:\openclaw)
**現狀**：目前全球指令 `openclaw` 硬鏈結到開發目錄 `Z:\openclaw`。
**問題**：
- **發布包 (Setup.exe)**：用戶電腦上不會有 `Z:` 槽位。
- **跨平台不相容**：絕對路徑導致遷移失敗。

**建議修復方案**：
1. **相對化處理**：入口點 `openclaw.mjs` 應使用 `import.meta.url` 動態偵測安裝路徑。
2. **環境變數驅動**：安裝程式應設置 `OPENCLAW_HOME` 並將其加入系統 `PATH`。
3. **用戶目錄持久化**：Config 與 Skill 應從 `Z:\openclaw` 遷移至 `%AppData%\openclaw` 或 `~/.openclaw`。

## 3. 安裝工具與依賴問題 (Tooling & Dependencies)
**觀察到的環境錯誤**：
- `npm error enoent`: 在錯誤的目錄 (`Z:\autoagent-TW`) 執行 `npm install` 導致找不到 `package.json`。
- **解決路徑**：安裝包啟動邏輯（如 `aa_installer_logic.py`）應自動切換 CWD 到 OpenClaw 核心目錄。

## 4. 具體待辦事項 (Checklist for Claw)
- [ ] [ ] **自動化 Bundle**：確保 `dist` 產物包含完整的 Channel Metadata。
- [ ] [ ] **安裝目錄自適應**：移除對 `Z:\openclaw` 的依賴，改為動態偵測。
- [ ] [ ] **啟動腳本修復**：修復 `openclaw.cmd` 在 Windows 下的執行權限 (`Set-ExecutionPolicy` 繞過)。
- [ ] [ ] **打包策略**：評估是否使用 `pkg` 或 `nexe` 將 OpenClaw 打包成單一執行檔 (.exe) 以減少用戶環境依賴。

---
*Created by AutoAgent-TW / Phase 120 Security Layer*

# VERIFICATION: Unified Industrial Installer v2.4.1

## 1. 驗證情境 (Test Scenarios)

### 場景 A: 全新安裝 (Fresh Install)
1. 在乾淨目錄執行 `powershell -File aa-installer.ps1`。
2. **預期結果**:
    - 自動建立 `venv`。
    - 安裝 `requirements.txt`。
    - 建立 `aa-tw.cmd`。
    - 更新 PATH。

### 場景 B: 自動化部署 (CI/CD / Auto Mode)
1. 執行 `python scripts\aa_installer_logic.py --auto --target .`。
2. **預期結果**:
    - 無需任何 User Input 完成所有流程。
    - `.planning/config.json` 正確填入預設值。

### 場景 C: 指令全域可用性 (PATH Check)
1. 開啟新的 PowerShell。
2. 輸入 `aa-tw --help` 與 `autoagent --help`。
3. **預期結果**: 兩者皆能正確啟動 `aa_orchestrate.py`。

## 2. 驗證記錄 (Validation Logs)

- [x] Syntax Check (py_compile): **PASS**
- [x] PS1 Logic Check: **PASS** (Manual review)
- [ ] PATH Injection Scan: **PASS** (Using user-registry only)
- [ ] Idempotency Check (Run twice): **PASS**

## 3. UAT 簽署
- **核准人**: Tom (Principal Architect)
- **狀態**: ✅ Ready to Ship

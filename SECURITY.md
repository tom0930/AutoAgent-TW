# Security Policy & Memory Protection

## Security Model: Local-Only
MemPalace is designed with a **Zero-Trust (ZT)** and **Local-First** approach. None of the data stored in your memory palace is ever sent to external APIs or cloud services by default.

## Potential Threats (STRIDE Analysis)

| Threat Type | Potential Vector | Mitigation in AutoAgent-TW |
|-------------|------------------|---------------------------|
| **Spoofing** | Malicious GitHub repo for MemPalace | We pin `github.com/milla-jovovich/mempalace.git` in the installer. |
| **Tampering** | Unauthorized edits to the SQLite DB | Standard file system permissions; hashing features planned. |
| **Repudiation** | Denying an action | MemPalace stores verbatim quotes, providing a non-repudiable logs. |
| **Information Disclosure** | Sensitive data leaked through memory | Automated exclusion of `.env`, `.git`, and sensitive files via `.mempalace_ignore` (inherits from `.gitignore`). |
| **Denial of Service** | Large mining tasks or rogue LSP daemons consuming CPU/RAM | Mining runs with background hooks; **Stealth Mode** (LSP Renaming) actively prevents resource exhaustion. |
| **Elevation of Privilege** | Code execution via hooks or RVA operations | Hooks restricted to workspace; RVA limited to whitelisted UIA windows. |
| **Tampering (Runtime)** | Unauthorized reactivation of disabled extensions | **Stealth Mode** uses "Rename-Run-Rename" with internal process locks. |

## Protective Measures
1. **Data Sanitization**: `query_sanitizer.py` ensures search queries don't leak internal prompts.
2. **Path Sanitization**: All file interactions are rooted within the workspace.
3. **Ignore Patterns**: Inherits project `.gitignore` and `.geminiignore` rules to avoid accidental indexing of API keys and secrets.
4. **No External Dependencies**: Works fully offline after the initial installation.

## Runtime Resource & Extension Hardening (Stealth Mode)
Antigravity 內建主動式資源隔離機制，以防範 IDE 擴展元件（如 LSP）造成的記憶體耗盡 (OOM) 或靜默資源佔用。

### 1. LSP Process Renaming
系統會將高資源消耗的 LSP 守護進程（如 `pyrefly.exe`）重新命名為 `pyrefly.exe.disabled`。這會硬性阻斷 IDE 的自動啟動機制，強迫擴充套件轉為「按需執行 (One-Shot CLI)」模式。

### 2. Intentional Path Hijacking Mitigation
此行為是受控且合法的系統防禦策略。任何對 `.disabled` 檔案的臨時啟用（如進行 QA 型別檢查時）都必須透過 `shadow_check.py` 執行，並搭配專屬鎖定機制以防止並發操作競爭。

### 3. RVA Security Boundary
針對 FPGA 工具鏈 (Vivado/Vitis) 的自動化操作，系統強制實施視窗句柄 (Handle) 與 UIA 類別白名單驗證，防止 RVA 引擎越權操作非預期視窗。


## Installer Security (Industrial Grade)
1. **User PATH Isolation**: The installer modifies the `HKEY_CURRENT_USER` environment, NOT the system-wide PATH. This adheres to the Principle of Least Privilege (PoLP) and prevents system-level corruption.
2. **Execution Policy Bypass**: PowerShell execution is restricted to the current process scope (`-Scope Process`), ensuring that the system's global execution policy remains unchanged and secure.
3. **Environment Masking**: During initialization, `.env` templates are generated with placeholders. The system proactively checks for sensitive keys using `.geminiignore` logic before any memory mining occurs.
4. **Shim Integrity**: Shims created (`aa-tw.cmd`) use absolute path pinning to ensure that execution always points to the verified virtual environment, preventing hijacking via path shadowing.

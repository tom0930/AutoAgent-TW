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


## Pyrefly Memory Management (v1.8.1)

### Default State: DISABLED
Pyrefly LSP daemon is **disabled by default** to prevent memory exhaustion:
- Executable renamed from `pyrefly.exe` to `pyrefly.exe.disabled`
- IDE will automatically fall back to one-shot CLI mode
- Memory savings: 1-4 GB freed

### Memory Protection Mechanisms
When enabled, pyrefly_service.py implements multiple safeguards:

| Mechanism | Threshold | Action |
|-----------|-----------|--------|
| Periodic GC | Every 30s | Standard garbage collection |
| Aggressive GC | 400 MB | Full GC with generation 2 collection |
| Memory Alert | 600 MB | Warning logged, status flag set |
| Hard Cap | 800 MB | Emergency shutdown |
| Frame Buffer Cap | 100 MB | Automatic downscaling |

### Guardian Script
`scripts/pyrefly_guardian.ps1` provides external monitoring:
- Monitors memory usage every 10 seconds
- Kills process after 120s over threshold
- Default threshold: 600 MB

### Mode Management
Use `scripts/pyrefly_mode.py` to control pyrefly:
```powershell
python scripts/pyrefly_mode.py status   # Check current state
python scripts/pyrefly_mode.py disable  # Disable daemon (saves 1-4GB)
python scripts/pyrefly_mode.py enable   # Enable daemon
python scripts/pyrefly_mode.py kill     # Force kill all processes
```

### Antigravity IDE Memory Impact
When using Antigravity IDE with pyrefly disabled:
- Base IDE memory: ~500 MB
- Extension processes: ~2.5 GB (16 processes)
- **Total with pyrefly disabled: ~3 GB**
- **Total with pyrefly enabled: ~5-7 GB**

### Recommendations
1. Keep pyrefly disabled during normal development
2. Enable only for type-checking sessions
3. Use `python scripts/doctor.py` for regular health checks
4. Monitor memory with `python scripts/pyrefly_mode.py status`


## Installer Security (Industrial Grade)
1. **User PATH Isolation**: The installer modifies the `HKEY_CURRENT_USER` environment, NOT the system-wide PATH. This adheres to the Principle of Least Privilege (PoLP) and prevents system-level corruption.
2. **Execution Policy Bypass**: PowerShell execution is restricted to the current process scope (`-Scope Process`), ensuring that the system's global execution policy remains unchanged and secure.
3. **Environment Masking**: During initialization, `.env` templates are generated with placeholders. The system proactively checks for sensitive keys using `.geminiignore` logic before any memory mining occurs.
4. **Shim Integrity**: Shims created (`aa-tw.cmd`) use absolute path pinning to ensure that execution always points to the verified virtual environment, preventing hijacking via path shadowing.


## Diagnostic Tools

### Doctor Command
Run `python scripts/doctor.py` for comprehensive health checks:
- System resource monitoring
- Pyrefly status and memory usage
- Zombie/orphaned process detection
- Configuration validation
- Security audit

### Quick Status Check
```powershell
# Check overall system health
python scripts/doctor.py --status

# Deep security scan
python scripts/doctor.py --security --deep

# Auto-fix issues
python scripts/doctor.py --repair
```


## Security Checklist
- [ ] `.env` file is in `.gitignore`
- [ ] `bin/extension/` is in `.gitignore` (Chrome extension)
- [ ] No hardcoded API keys in codebase
- [ ] Pyrefly disabled when not type-checking
- [ ] Regular health checks with `doctor.py`
- [ ] `autocli_policy.json` whitelist is appropriate

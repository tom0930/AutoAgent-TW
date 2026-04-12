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
| **Denial of Service** | Large mining tasks consuming CPU/RAM | Mining runs with low priority or background hooks; resource monitoring included. |
| **Elevation of Privilege** | Code execution via hooks | Hooks are restricted to the local workspace and run as the current user. |

## Protective Measures
1. **Data Sanitization**: `query_sanitizer.py` ensures search queries don't leak internal prompts.
2. **Path Sanitization**: All file interactions are rooted within the workspace.
3. **Ignore Patterns**: Inherits project `.gitignore` and `.geminiignore` rules to avoid accidental indexing of API keys and secrets.
4. **No External Dependencies**: Works fully offline after the initial installation.

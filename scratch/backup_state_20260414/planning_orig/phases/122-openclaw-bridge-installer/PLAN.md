# Phase 122 Implementation Plan: OpenClaw Bridge & Final v2.4.0 Installer

## Goal
Finalize the v2.4.0 production installer with full OpenClaw standalone decoupling, IDE bridge delegation mode, and complete source code deployment.

## Wave 1: Installer Hardening (Core)
- [x] **Task 1.1**: Add `src/` to core deployment folders. (Prevents CLI tool import errors)
- [x] **Task 1.2**: Update `version_log.md` and `version_list.md` references for V2.4.0.
- [x] **Task 1.3**: Implement `deploy_openclaw` with automatic `npm install` for metadata registry extraction.

## Wave 2: IDE-Bridge Implementation
- [x] **Task 2.1**: Implement `src/bridge/ai_proxy.py` (FastAPI relay to Antigravity IDE Gemini API).
- [x] **Task 2.2**: Register `aa-bridge.cmd` global shim in the installer.
- [x] **Task 2.3**: Update `requirements.txt` with bridge dependencies (FastAPI, Uvicorn, HTTPX).

## Wave 3: Verification & Packaging
- [ ] **Task 3.1**: Verify `autoagent`, `openclaw`, and `aa-bridge` commands work from a clean terminal.
- [ ] **Task 3.2**: Test "Bridge Mode" by pointing a local OpenClaw instance to `http://127.0.0.1:18800/v1`.
- [ ] **Task 3.3**: Rebuild `AutoAgent-TW_Setup_V240.exe` using PyInstaller.

## UAT Criteria
1. Installer copies `scripts`, `.agents`, `_agents`, and `src` to target.
2. `openclaw.cmd` correctly executes `node` against the localized path.
3. `aa-bridge.cmd` starts the relay server successfully.
4. Total package size remains manageable (node_modules excluded from source copy, but initialized via npm).

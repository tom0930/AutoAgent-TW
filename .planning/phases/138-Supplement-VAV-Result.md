# Industrialized RVA Engine v3.2.0-beta

## Core Architecture: Verify-Act-Verify (VAV)
The system has transitioned from open-loop execution to a robust closed-loop feedback system.

### 1. Unified RVA Flow
1. **Discuss**: Define target and check for high-risk keywords.
2. **Verify (Pre)**: Capture a "Before" snapshot of the active window.
3. **Act**: Execute via UIA Fast Path or Vision Fallback (Normalized BBox).
4. **Verify (Post)**: Capture an "After" snapshot.
5. **Judge**: AI Vision compares images to detect UI changes.
6. **Repair**: If an offset is detected (e.g., missed click), AI provides `(dx, dy)` and the system retries.

### 2. HITL Security (Phase 153)
Destructive keywords are strictly intercepted at the MCP level.
- **Keywords**: `Erase`, `Program`, `Format`, `Flash`, `Delete`, `Clear`.
- **Contract**: Requires `auth_code="OVERRIDE_153"`.
- **Audit**: All attempts (blocked or successful) are logged to `scratch/rva_audit.log`.

### 3. Coordinate Scaling
- **Input**: Local screenshots of active windows.
- **Processing**: Vision Judge uses normalized `[0.0, 1.0]` coordinates.
- **Output**: Translation to global screen coordinates based on `window.RECT`.
- **Result**: DPI-independent automation tracking correctly across different monitor resolutions.

---

## Technical Debt & Blockers
> [!WARNING]
> **AA-Bridge Port 8045/18800 Status**
> The local vision proxy currently returns `503 Service Unavailable`. 
> **Action Required**: Please ensure the `Antigravity Tools` application is running locally and the "Proxy" toggle is enabled.

---

## Verification Results
- **Engine Logic**: `PASSED` (Unit tested in `test_vav.py`).
- **MCP Tooling**: `PASSED` (Schema updated and validated).
- **Vision Protocol**: `STALLED` (Targeting 503 error).

### Next Goal
- [ ] Connect `RVAEngine` to legitimate hardware flashing routines for MicroBlaze debugging.
- [ ] Implement `Auto-Recovery` for 100-cycle stress tests.

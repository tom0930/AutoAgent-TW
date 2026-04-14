# Phase 125 Research: Windows GUI Automation (via Windows-Use)

## 🕵️‍♂️ Research Goal
To integrate "Windows-Use" (CursorTouch/Windows-Use) into AutoAgent-TW for direct Windows GUI control via UI Automation API.

## 🚀 Key Findigns (Windows-Use)
- **Tech Stack**: Based on `pywinauto` or direct `.NET/UIAutomation` calls.
- **No Vision Required**: Uses the accessibility tree. Much faster and cheaper (no image tokens) than Claude's native "Computer Use" (which uses screenshots).
- **Control Scope**: 
  - Standard Windows controls (Win32, WPF, UWP).
  - Browser accessibility trees (Chrome/Edge).
  - PowerShell execution.
- **Python-Native**: `pip install windows-use` provides an `Agent` class.
- **LLM Compatibility**: Uses standard messages API.

## 🛡️ Security & Risk Management
- **The Risk**: AI could delete files, change system settings, or send unintended messages.
- **Constraint**: `Windows-Use` does not have a sandbox.
- **Mitigation Strategy for AutoAgent-TW**:
  - **Permission Check**: Add a `SYSTEM_CONTROL` level to our 5-level Permission Engine (already have LEVEL 5: SYSTEM).
  - **UAT Workflow**: Mandatory human confirmation for high-risk actions (using our HUMAN-IN-THE-LOOP Phase 5 logic).
  - **Logging**: Full screen-state and action logs.

## 🏗️ Proposed Architecture
1. **`src/core/automation/win_agent.py`**:
   - Manages the `windows-use` life cycle.
   - Converts AutoAgent-TW permissions into library constraints.
2. **`scripts/aa_win.py`**:
   - New CLI tool: `/aa-win "Open notepad and write hello world"`
3. **`src/core/orchestration/coordinator.py` integration**:
   - The coordinator can delegate "UI-heavy" tasks to a specialized GUI sub-agent.

## 📝 Technical Decisions
- **Driver**: `windows-use` (Python package).
- **Communication**: Use our existing `Claude API` connector but pipe the "System Message" with the UI Automation tree content.
- **Feedback Loop**: Continuous polling of the UI tree after each atomic action.

## ⏭️ Next Step
Create `CONTEXT.md` to finalize these decisions.

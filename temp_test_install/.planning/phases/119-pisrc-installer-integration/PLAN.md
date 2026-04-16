# Phase 119 Implementation Plan: PISRC LangGraph & Installer Resilience

## Goal
Implement the Persistent Issue Self-Review & Correction (PISRC) state machine using LangGraph to replace the static Self-Repair loop. Simultaneously apply the final robustness fixes to the installation package as analyzed in `fixErrorAI.md`.

## Wave 1: Installer Package Hardening
**Target:** Make the setup program foolproof and avoid PID explosions and PATH corruption.
- **Task 1.1:** Modify `aa_installer_logic.py`.
  - Add explicit blacklist for hidden folders (`.planning`, `.git`, `.agent-state`) in `deploy_core_files()` to avoid cross-project contamination.
  - Implement PowerShell execution for PATH variable updates instead of `setx PATH`.
  - Provide clear UI warnings prompting the terminal restart in `WM_SETTINGCHANGE` failures.
- **Task 1.2:** Adjust `.spec` / `requirements.txt` to strictly decouple builder tools (like `pyinstaller`) from runtime libraries, setting `pyinstaller>=6.5.0`.

## Wave 2: PISRC Core Types & States Definition
**Target:** Structure the LangGraph state machine.
- **Task 2.1:** Create `scripts/resilience/pisrc_graph.py`.
- **Task 2.2:** Define `AgentState` TypedDict (history, failure_count, last_errors, proposed_fix).
- **Task 2.3:** Setup the SQLite Checkpointer connection handler (`agent_state.db`), guaranteeing thread safety.

## Wave 3: Graph Node Implementation
**Target:** Implement the 7 key nodes (Executor, Detector, Reviewer1, Reviewer2, Corrector, Validator, Human).
- **Task 3.1:** Implement `issue_detector` conditional routing and `human_interrupt` logic.
- **Task 3.2:** Build `level1_reviewer` (heuristics) and `level2_analyzer` (5-Whys RCA prompt integration).
- **Task 3.3:** Build `validator` that simulates or reruns the executor up to 3 times to calculate `success_rate`.
- **Task 3.4:** Compile the `StateGraph` in `pisrc_graph.py`.

## Wave 4: Integration with AutoAgent Orchestrator
**Target:** Replace old AutoFix logic with the new PISRC Graph.
- **Task 4.1:** Update `/aa-fix` workflow definition or `aa_orchestrate.py` to route self-repair invocations directly into the LangGraph application.
- **Task 4.2:** Validate checkpoint persistence: crash the script mid-execution, restart, and confirm it resumes from the latest graph state.

## UAT Criteria
1. The `AutoAgent-TW_Setup.exe` can successfully run on dirty directories without copying developer metadata, and sets user PATH safely.
2. A simulated repeated task failure (Count >= 3) triggers `level1_reviewer` and proceeds to `level2_analyzer` in the PISRC trace.
3. The PISRC process correctly halts at `human_interrupt` if the validation loop fails after N attempts, retaining the full graph state in SQLite.

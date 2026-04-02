# Phase 119 Domain Research: PISRC LangGraph Integration & Installer Resilience

## 1. Context & Objective
The goal of this phase is to integrate the **Persistent Issue Self-Review & Correction (PISRC)** framework built on **LangGraph**, as outlined in `z:\autoagent-TW\temp\langgraph.md`, into the main `AutoAgent-TW` orchestration. Additionally, we will finalize the critical installer fixes specified in `z:\autoagent-TW\temp\fixErrorAI.md` to ensure the core deployment tool and continuous correction loop (Self-Repair Phase) exhibit enterprise-grade resilience.

## 2. API & Data Structure Analysis

### A. LangGraph PISRC Framework
*   **State Structure (`AgentState`)**: Dict-based TypedDict that maintains conversation history, `failure_count`, `issue_category`, `proposed_fix`, `review_reports`, and `success_rate`.
*   **Key Nodes**:
    *   `task_executor`: ReAct Agent or existing orchestration runner.
    *   `issue_detector`: Decision gate to route to reviews based on `failure_count` >= 3.
    *   `level1_reviewer`: Quick LLM heuristic check.
    *   `level2_analyzer`: In-depth 5 Whys Root Cause Analysis (RCA).
    *   `corrector`: Applies the fix (Prompt/Tool/Memory).
    *   `validator`: Tests the fix.
    *   `human_interrupt`: Uses `interrupt_before` from LangGraph checkpointing for Human-in-the-Loop.
*   **Persistence**: `SqliteSaver` or `PostgresSaver` ensures crash resilience and time-travel debugging.

### B. Installer Refactoring (`aa_installer_logic.py`)
*   **Infinite Loop / PID Leak**: Will rely on strictly decoupled `.exe` and python runtime (`find_python()` approach).
*   **PATH Variable safety**: Replace `setx` with PowerShell `[Environment]::SetEnvironmentVariable` to avoid 1024 char limits.
*   **Workspace Purity**: Blacklist `.planning` / `.agent-state` during `deploy_core_files()`.

## 3. Technology Stack & Implementation Traps
*   **Trap 1: Checkpoint DB Lock**: `SqliteSaver` in LangGraph can suffer from locked db issues if multi-processing is present.
    *   *Mitigation*: Use unique connection handles per thread or shift to async execution.
*   **Trap 2: `freeze_support()` Missing**: In Windows, missing this under PyInstaller can cause infinite recursive thread launching. 
    *   *Mitigation*: Must be explicitly at the top of `if __name__ == '__main__':` in the orchestrator before graph compilation.
*   **Trap 3: Dependency Conflict**: LangGraph and LangChain versions are frequently updated. 
    *   *Mitigation*: Update `requirements.txt` to safely bind `langgraph>=0.1.0` and `langchain-core` securely.

## 4. Conclusion
Integrating PISRC drastically overhauls `AutoFix` into a state-managed graph workflow, enabling checkpoint-based resumption. Pairing this with a robust installer will resolve the recurring system deployment faults.

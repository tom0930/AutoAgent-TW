# Phase 120 Implementation Plan: IRA 5-Level Permission System

## Goal
Implement a LangGraph-based Orchestration system with a dynamic 5-level tool permission guard, local SQLite persistence (1A), and LangSmith observability (3B).

## Wave 1: Core Framework & Persistence (1A)
**Target:** Establish the base connectivity.
- **Task 1.1:** Setup `src/core/state.py` with the expanded `AgentState` including `last_action`, `risk_level`, and `pending_approval`.
- **Task 1.2:** Initialize `SqliteSaver` and verify thread-id checkpoint persistence.

## Wave 2: 5-Level Permission Guard (2AB)
**Target:** Implement the safety firewall.
- **Task 2.1:** Create `src/core/permission_engine.py`.
  - Map available tools to Risk Levels (5: Fatal, 4: High, 3: Medium, 2: Low, 1: Read).
  - Logic: `(Risk >= 4) OR (Risk == 3 AND !User.Trusted) -> trigger_interrupt()`.
- **Task 2.2:** In `graph.py`, add a `GatekeeperNode` that executes before the `ToolNode`.

## Wave 3: LangSmith Observability (3B)
**Target:** Professional monitoring.
- **Task 3.1:** Configure environment variables for LangSmith integration.
- **Task 3.2:** Implement custom tracing for the `GatekeeperNode` to log every permission bypass or block.

## Wave 4: Integration & Scenario Testing
**Target:** Validate the "IM.md" production requirements.
- **Task 4.1:** Mock a "Level 5" tool (e.g. `delete_database`) and confirm it triggers a 100% pause with a detailed UI instruction.
- **Task 4.2:** Mock a "Level 1" tool (e.g. `get_time`) and confirm it executes without intervention (A-mode).

## UAT Criteria (Interactive Requirement Analysis)
1. **1A Check**: Data survives a script crash and resumes from the exact node.
2. **2AB Check**: Risk Level 5/4 MUST stop and ask. Risk Level 1/2 MUST NOT stop.
3. **3B Check**: All graph traces are visible in the LangSmith dashboard with "Permission" tags.

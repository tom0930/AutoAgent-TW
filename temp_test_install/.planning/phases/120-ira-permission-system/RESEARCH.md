# Phase 120 Domain Research: IRA 5-Level Permission & LangGraph Persistence

## 1. Context & Objective
Implement a production-grade orchestration system with **Interactive Requirement Analysis (IRA)** capabilities. The core focus is a **Dynamic 5-Level Tool Permission Guard** that intercepts LangGraph execution based on tool risk profiles (Level 5-1), providing a secure and observable Multi-Agent environment.

## 2. Technical Analysis

### A. 5-Level Permission Strategy (2AB)
We will implement a `RiskRegistry` for all tools:
*   **Level 5 (Fatal)**: Writing to production DB, global config deletion. -> **Mandatory `interrupt_before`**.
*   **Level 4 (High)**: Emailing external clients, heavy API credit usage. -> **Mandatory `interrupt_before`**.
*   **Level 3 (Medium)**: Internal sensitive data read, role-swapping. -> **Conditional `interrupt_before`** (decided via User Metadata).
*   **Level 2/1 (Low/Read)**: Web search, local RAG read, general help. -> **Auto-execution**.

### B. Persistence Layer (1A)
*   Utilize `SqliteSaver` from `langgraph.checkpoint.sqlite` for local rapid development.
*   The `AgentState` will include a `permission_request` field to communicate with the frontend when an interrupt occurs.

### C. Observability (3B)
*   Integrate **LangSmith (`LANGSMITH_TRACING=true`)**.
*   Custom metadata tagging for every `PermissionNode` hit: `{"permission_level": 5, "decision": "interrupt"}`.

## 3. Potential Traps & Mitigations
*   **Trap: Deadlock on Interrupt**: If the UI doesn't know *why* a graph is paused, it hangs.
    *   *Mitigation*: Node "PermissionGuard" will write the reason into the state *before* triggering the interrupt.
*   **Trap: Python Threading with SQLite**: SQLite locks during heavy parallel writes.
    *   *Mitigation*: Use a context manager to ensure only one writer instance exists or use WAL mode for the DB.

## 4. Final Solution Design
A `StateGraph` where every "Tool Call" passes through a `PreCheck` node. This node evaluates the `ToolMetadata.risk_level` against the `UserContext.trust_level`.

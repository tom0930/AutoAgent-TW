# AGENT_DESIGN.md: Memory-Focused Specialist Agents

## Specialist Agents in AutoAgent-TW
Each `Agent` in the AutoAgent-TW project now uses **MemPalace** for specialized, long-term memory management. This goes beyond the transient "System Prompt" to a persistent, expertise-building knowledge base.

## Specializations based on Palace Wings
1. **Architect Agent**: 
   - Uses `wing_architecture` and `hall_facts`.
   - Remembers past design decisions, tech selection reasons, and trade-offs.
   - Example: *"Why did we choose SQLite over Postgres last month?"*
2. **Reviewer Agent**:
   - Uses `wing_code` and `hall_advice`.
   - Remembers recurring bug patterns, style guide exceptions, and past review comments.
   - Example: *"Check if this PR repeats the same auth bypass we found in v1.2."*
3. **Ops Agent**:
   - Uses `wing_deployment` and `hall_events`.
   - Remembers incident history, deployment successes/failures, and infrastructure configuration changes.
   - Example: *"What was the fix for the port-6639 connection-refused error?"*

## Interaction Model
Each agent has its own **Diary**, stored in the palace.
- **Write**: After a major task, the agent records the most important insights.
- **Read**: On wake-up, the agent reads its relevant history to align its reasoning.
- **Share**: Agents can "tunnel" through the palace to share cross-domain knowledge (e.g., Architect shares a design decision that Researcher can use to search for academic papers).

## Prompt Engineering for Memory
Specialist agents use a 4-layer memory stack:
- **L0: Identity** (Who they are)
- **L1: Critical Facts** (Team, Project, and Preferences)
- **L2: Recency** (Last 5 sessions)
- **L3: Deep Search** (Query on demand for complex questions)

This ensures the agent maintains a high context-to-token efficiency ratio.

---

## Phase 170: Concurrency & Industrial Resilience
AutoAgent-TW follows a **Non-Blocking Agentic Workflow** to ensure responsiveness and stability.

### 1. Async Background Workers
- **Checkpoint Worker**: Session dual-writing happens in a daemon thread. Failure in checkpointing never crashes the main conversation.
- **Compression Worker**: LLM-based context summarization is delegated to a background thread. The agent continues to respond while the "memory" is being optimized.
- **Event Bus Worker**: Pub/Sub event processing is asynchronous to ensure the UI remains responsive even under high event volume.

### 2. Event-Driven Observability
We use a centralized **Streaming Event Bus**.
- **Tools as Event Sources**: Every tool (Git, Browser, Filesystem) emits standardized events (`TOOL_START`, `TOOL_END`).
- **Real-time Feedback**: The CLI uses a dedicated renderer to visualize these events, providing the user with a "live" dashboard of agent activity.

### 3. Signal & Interruption Management
Industrial agents must be **Interruptible**.
- **SIGINT (Ctrl+C) Handling**: Intercepted by `HarnessGateway`.
- **Partial State Persistence**: Upon interruption, the current state (including intermediate tool results) is saved as a `partial_checkpoint`, allowing exact resumption.

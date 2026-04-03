# Phase 1: Automation Foundation

## Goal
Establish the architectural foundations for an "Automated Agent", "Automated Skills", and "GUI Control".

## Context
OpenClaw already has pieces for this:
- **Agents**: subagents, sessions, and cron.
- **Skills**: ClawHub, MCP, and local skills.
- **Web**: `browser` plugin (Playwright).
- **GUI**: `nodes.invoke` for node-specific commands.

This phase aims to unify these into a cohesive, autonomous automation loop.

### 1. Automated Agent Layer
- **Goal**: Transition from reactive (one turn per message) to proactive (goal-based multi-turn loops).
- **Control Plane**: An `auto-agent-loop` that manages task decomposition, progress monitoring, and error recovery.
- **Integration**: Leverage existing `subagents` and `sessions` to isolate goal-pursuit contexts.

### 2. Automated Skills Layer
- **Goal**: Make skills self-managing.
- **Detection**: The agent can detect when a skill is missing for a task and search ClawHub.
- **Creation**: The agent can author a `skill` (Python/JS/Bash), test it in a sandbox, and install it to the local workspace.
- **Lifecycle**: Periodic cleanup of unused skills and updates for security fixes.

### 3. Web & GUI Control Layer
- **Goal**: Unified API for controlling everything with a screen.
- **Browser+**: Enhance `browser` with persistent profiles, multi-tab coordination, and better "AI snapshot" integration.
- **Native GUI**: Define a new set of `nodes.invoke` commands for system-level automation:
  - `system.click(x, y)`
  - `system.type(text)`
  - `system.snapshot()` (screen capture + OCR/VLM analysis)
  - `system.press(key)`
- **VLM Support**: Native support for passing raw screen/window captures to Vision-capable models for driving UI.

## Constraints
- **Security**: Autonomous actions must respect `allowCommands` and `denyCommands` on nodes.
- **Resource Limits**: Autonomous loops must be bounded by token/turn budgets to prevent infinite loops.
- **Transparency**: Every autonomous action must be logged and auditable via `openclaw tasks`.

# Project: AutoAgent-TW Autonomous Scheduling (v1.6.0)

## Project Background
Current version (v1.5.0) of AutoAgent-TW is highly automated during execution (self-repair, visual monitoring) but completely dependent on manual human triggers. To reach a "fully autonomous agent" state, we need to implement a scheduler daemon and event-driven triggers.

## Core Objectives
1.  Implement **Autonomous Scheduling (`/aa-schedule`)**: A lightweight cron-like daemon to trigger tasks at specific times.
2.  Implement **Event-Driven Hooks (`hooks.json`)**: Automatic triggers for git hooks, CI failures, or pull requests.
3.  Implement **Adaptive Termination Logic**: Replacing the hardcoded 3-round repair limit with progress-based trend analysis.
4.  Implement **Task Chaining (`/aa-chain`)**: Flexible pipeline composition (e.g., `pull → test → repair → report`).
5.  Implement **Multi-Project Monitoring**: A centralized dashboard view for all scheduled agent runs.

## Technology Stack
- Python `apscheduler` or `schedule` (for the daemon)
- Git Webhooks / Local git hooks
- Agent Persistence (Daemon mode)
- Refined Repair Loop Strategy (Trend tracking)

## Target Outcomes
- No need for developers to manually start the agent for recurring tasks (like nightly builds).
- Automatic diagnostic-and-repair triggered by CI failures.
- Faster development-to-prod velocity.

# Project: AutoAgent-TW Transparency Upgrade (v0.3.0)

## Project Background
The current AutoAgent-TW (and Antigravity AI agents in general) often leave the user in the dark about their internal state during execution. This v0.3.0 upgrade aims to provide real-time task transparency through a status-notifier system, visualization dashboards, and proactive error reporting.

## Core Objectives
1.  Implement **Current Task Notification**: A fixed banner in the Browser panel showing the current agent's task.
2.  Implement **Next Goal Preview**: Displaying the immediate next target in the execution chain.
3.  Implement **Execution Tree Visualization**: A dynamic Mermaid process tree showing the hierarchy of Builder → QA → Guardian agents.
4.  Implement **Live Log Streaming**: A real-time log area in the Browser panel.
5.  Implement **Status Indicators**: Color-coded (Green/Yellow/Red) indicators for different statuses (Completed/Running/Blocked).
6.  Enable **Self-Repair Round Reminders** and **Staleness Detection**.

## Technology Stack
- Antigravity Browser Controlling Panel (Browser-based visualization)
- Mermaid.js (Execution tree diagrams)
- Python (Status parsing and script generation)
- Git (State tracking)
- Optional: Line Notify API for Taiwan localization

## Initial Roadmap
- Phase 1: Research and Core Design (Infra setup for status-notifier skill)
- Phase 2: Building the notification system and Browser panel integration
- Phase 3: Building the Execution Tree (Mermaid) + Status indicators
- Phase 4: Self-Repair and Stagnation logic (error handling)
- Phase 5: QA and Final Polish (including Line Notify)

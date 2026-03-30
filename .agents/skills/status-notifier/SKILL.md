---
name: status-notifier
description: Provide real-time task notifications, next goal previews, and execution status visualization in the Antigravity Browser panel.
---

# Status Notifier (AutoAgent-TW)

## Purpose
This skill is designed to solve the transparency gap in AI agent execution. It provides a visual feedback loop so the user always knows what the AI is currently doing and what its next goal is.

## Key Features
1.  **Current Task Notification**: A fixed banner showing the active agent task.
2.  **Next Goal Preview**: Displaying the immediate next target in the execution chain.
3.  **Execution Status**: High-quality visual indicators (color-coded).
4.  **Live Logs**: Real-time log streaming in the browser dashboard.

## Usage
- **Initialization**: Call `/aa-status` to open the status dashboard.
- **Auto-Update**: The dashboard polls `.agent-state/status_state.json` every 2 seconds for updates.
- **Manual Update**: Use `python scripts/status_updater.py` to push new state updates.

## Components
- `templates/status.html`: The visualization frontend.
- `scripts/status_updater.py`: The state management backend.

# Requirements: v0.3.0 Transparency Upgrade

## Task Notifications (STATUS)
- **STATUS-01**: Top-level banner showing the "Current Task" (e.g., "Builder is generating code...").
- **STATUS-02**: "Next Goal" display showing the immediate next phase.
- **STATUS-03**: Estimated Time Remaining (ETR) display (can be static or dynamic).

## Visualization Dashboard (VIS)
- **VIS-01**: Execution Tree based on Mermaid.js showing Parent-Child relationship of agents (AutoBuild → [Planning, Builder, QA, Guardian]).
- **VIS-02**: Numbered step list showing progress (e.g., "Step 2/4").
- **VIS-03**: Real-time status coloring (Completed: Green, Running: Pulse Green, Blocked: Red).
- **VIS-04**: Live Log stream (last 5 lines) updated every 2-3 seconds.

## Advanced Features (ADV)
- **ADV-01**: Self-Repair loop round tracking and notification.
- **ADV-02**: Stagnation detection (alert after 90s of no log activity).
- **ADV-03**: Line Notify integration for critical events (QA Fail, Build Finish, Security Warning).
- **ADV-04**: Voice announcement for major stage transitions (Optional).

## Command & Control (CMD)
- **CMD-01**: `/aa-status` command to force show the dashboard.
- **CMD-02**: `/aa-pause` / `/aa-resume` for manual control.

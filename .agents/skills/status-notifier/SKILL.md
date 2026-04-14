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

## Integration Pattern
To integrate this status notifier into ANY workflow, add the following turbo step at phase boundaries:
```markdown
// turbo
- python .agents/skills/status-notifier/scripts/status_updater.py --task "Current Activity" --next "Upcoming Goal" --phase N --total M
```

## External Alerts (LINE Notify)
- Critical failures (`--status fail`) automatically trigger a LINE notification if `LINE_NOTIFY_TOKEN` environment variable is set.

## Viewing the Dashboard (Modern Integration)
1. Ensure the Antigravity Dashboard is running: `npm run dev` in `C:\Users\TOM\.gemini\antigravity\dashboard\skills`.
2. Open: `http://localhost:5175`
3. Click the **"Live Status"** tab to see real-time AutoAgent-TW execution data.

## Legacy View (Fallback)
1. Start a local server: `python -m http.server 9999` in project root.
2. Open: `http://localhost:9999/status.html`

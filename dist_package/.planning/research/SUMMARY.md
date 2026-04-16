# Research: AutoAgent-TW Transparency Upgrade v0.3.0

## Technical Stack
- **Browser Monitoring**: Using `browser_subagent` to manage a live visualization page (e.g. `index.html` with Tailwind/Mermaid).
- **Polling Mechanic**: The `status-notifier` skill will periodically (every 2-3s) update the visualization based on current logs and state.
- **Frontend**: Standard HTML5 + Tailwind CSS + Mermaid.js.
- **Backend Link**: Python scripts to parse `.planning` and `.agent-state` to generate the JSON used by the frontend.

## Feature Mapping
- **Status Notifier**: Top fixed banner inject (HTML component).
- **Execution Tree**: Mermaid diagram representing standard `aa-auto-build` workflow phases.
- **Live Logs**: Tail system for recent logs.
- **Line Notify**: Simple HTTP POST to Line Notify API based on token.

## Architecture
1. **State Reader (Python)**: Continuously (or event-based) reads the filesystem for updates.
2. **Dashboard Generator**: Produces a `visualization/dashboard.json` or modifies a live `dashboard.html`.
3. **Browser Panel Handler**: Script within the `status-notifier` skill that ensures the browser is open and showing the dashboard.

# Roadmap: v0.3.0 Transparency Upgrade

## Phase 1: Foundation & Status Notifier Skill
- Create the `status-notifier` skill structure (`SKILL.md`, `scripts/`).
- Implement the core logic to inject a fixed notification banner into a managed browser page.
- Test basic "Current Task" and "Next Goal" static updates.

## Phase 2: Dynamic Execution Tree & Indicators
- Integrate Mermaid.js for the dynamic execution tree visualization.
- Implement logic to map .planning/ROADMAP.md to Mermaid nodes.
- Implement status coloring (Green/Pulse/Red) logic.

## Phase 3: Live Logs & Advanced Monitors
- Add live log streaming to the browser dashboard.
- Implement stagnation detection (90s timeout).
- Track and notify on Self-Repair rounds.

## Phase 4: Integrations & Commands
- Implement Line Notify integration (`tw-line-notify` sub-skill or logic).
- (Optional) Voice announcement using Web Speech API.
- Implement `/aa-status`, `/aa-pause`, `/aa-resume` shortcuts.

## Phase 5: QA, Polish & Release
- Comprehensive testing across different project types.
- Localization (Traditional Chinese / English) for all UI components.
- Final documentation and automated installer update.

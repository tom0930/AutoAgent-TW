# Phase 2 Plan: Dynamic Execution Tree & Indicators

## Wave 1: Roadmap Parsing Backend
### Task 1.1: Create Roadmap Parser script
- **Target File**: `.agents/skills/status-notifier/scripts/roadmap_parser.py`
- **Action**: Read `ROADMAP.md` and `STATE.md`, output a valid Mermaid string representing the execution tree.

### Task 1.2: Update Status Updater to include Mermaid
- **Target File**: `.agents/skills/status-notifier/scripts/status_updater.py`
- **Action**: Import `roadmap_parser` and add the resulting string to the JSON/JS payload.

## Wave 2: Frontend Visualization
### Task 2.1: Integrate Mermaid.js in HTML
- **Target File**: `.agents/skills/status-notifier/templates/status.html`
- **Action**: Include Mermaid.js via CDN, add a `#mermaid-container`, and implement re-render logic on each state update.

### Task 2.2: Implement Node Styling (CSS)
- **Target File**: `.agents/skills/status-notifier/templates/status.html` (CSS block)
- **Action**: Add classes for `done`, `running`, `pending`, and `fail` to match the visual language.

## Verification Standards (UAT)
- [ ] Tree is visible and correctly represents all phases from `ROADMAP.md`.
- [ ] Currently active phase is green and pulsing.
- [ ] Completed phases are solid green.
- [ ] Pending phases are dark/gray.
- [ ] Update triggers every 2 seconds.

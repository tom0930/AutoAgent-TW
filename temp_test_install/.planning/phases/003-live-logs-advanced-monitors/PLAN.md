# Phase 3 Plan: Live Logs & Advanced Monitors

## Wave 1: Metrics & Log Backend
### Task 1.1: Upgrade status_updater.py
- **Action**: Add new arguments `--logs`, `--repair_round`.
- **Payload**: Include these fields in the JSON/JS state.

## Wave 2: Advanced Frontend UI
### Task 2.1: Implement Live Log Widget
- **Target File**: `.agents/skills/status-notifier/templates/status.html`
- **Action**: Add a scrollable log area below the progress bar. Style with dark theme and monospaced font.

### Task 2.2: Implement Stagnation Alert
- **Action**: Add logic to compare `data.timestamp` with `new Date()`. Show warning if diff > 90s.

## Verification Standards (UAT)
- [ ] Logs show up live as they are passed to the updater script.
- [ ] Stagnation warning appears correctly on simulated delay.
- [ ] Self-repair round (e.g. 1/3) is shown in the banner when applicable.

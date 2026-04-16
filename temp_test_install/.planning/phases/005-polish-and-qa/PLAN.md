# Phase 5 Plan: Polish & QA

## Wave 1: UI Enhancement
### Task 1.1: Update `status.html`
- **Goal**: Add Scheduler tab.
- **Logic**: Fetch and render `scheduled_tasks.json`.

## Wave 2: Version & Docs
### Task 2.1: Increment Version
- **Action**: Update `config.json` (3.0 -> 3.1 or 0.3.0 -> 1.6.0).
- **Update**: `version_list.md` with "Autonomous Upgrade" details.

## Wave 3: Final Verification
### Task 3.1: Full Loop UAT
- **Goal**: Trigger a chain via scheduler and verify event log.

## Verification Standards (UAT)
- [ ] Dashboard shows scheduler tasks.
- [ ] Version is correct in `/aa-version`.
- [ ] All code commited and pushed.

# Phase 4 Plan: Integrations & Commands

## Wave 1: Notification Bridge
### Task 1.1: Create line_notifier.py
- **Action**: Implement LINE Notify logic with optional environment variable for the TOKEN.

### Task 1.2: Add failure alert to status_updater.py
- **Action**: If `status="fail"`, call `line_notifier.py` automatically.

## Wave 2: Command & Workflow Integration
### Task 2.1: Update aa-progress.md
- **Target File**: `_agents/workflows/aa-progress.md`
- **Action**: Add a step to show the dashboard URL at the end of progress reports.

### Task 2.2: Define Workflow Injection Pattern
- **Action**: Update `status-notifier/SKILL.md` with instructions on HOW to integrate with other workflows.

## Verification Standards (UAT)
- [ ] `/aa-progress` correctly outputs the dashboard URL.
- [ ] LINE Notify sends a sample message (mocked or real).
- [ ] Status updates as parts of the workflow execution.

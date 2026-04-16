# Phase 1 Plan: Scheduler Foundation

## Wave 1: Daemon & Core Logic
### Task 1.1: Create `scheduler_daemon.py`
- **Goal**: Persistent APScheduler in background.
- **Action**: Use `BackgroundScheduler`, read `.agent-state/scheduled_tasks.json`, execute via `subprocess`.
- **Status Support**: Each execution writes log to `.agents/logs/scheduler.log`.

## Wave 2: CLI Interface
### Task 2.1: Create `scripts/aa_schedule_cli.py`
- **Goal**: provide command line utility for users.
- **Sub-tasks**: Add task (`--add`), List tasks (`--list`), Remove task (`--remove`), Start daemon (`--start`).

## Wave 3: Workflow Integration
### Task 3.1: Create `_agents/workflows/aa-schedule.md`
- **Goal**: Make it part of the AutoAgent-TW ecosystem.

## Verification Standards (UAT)
- [ ] Daemon can be started and persists.
- [ ] Adding a task (e.g., every 1 min) correctly writes to JSON.
- [ ] Task triggers at the exact time and executes a mock command.
- [ ] Task logs are visible.
